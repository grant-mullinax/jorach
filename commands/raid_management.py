import discord
from discord.ext import commands

from providers.jorach_bot import *
from schema.constants import *
from sheets.client import *



class Management(commands.Cog):

    """
    `Management` is a class that allows admin users to create raids for users
    """
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def bootstrap(self, ctx):
        """

        DEVELOPER INFO:
        Bootstraps the channels for welcoming new users if necessary.
        """
        # First, let's create the category if it's not already there.
        category = await self.create_category_if_not_exists(ctx, START_HERE_CATEGORY)

        # Do nothing if the channel is already made
        for c in category.channels:
            if c.name == START_HERE_CHANNEL:
                return

        channel = await category.create_text_channel(START_HERE_CHANNEL)

        await self._post_add_identity_embed(channel)
        await self._post_edit_identity_embed(channel)
        await self._post_remove_identity_embed(channel)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def startraid(self, ctx):
        """
        Starts a new raid (admin only)

        DEVELOPER INFO:
        :param ctx: The context of invocation for the command that sheet was ran on.
        """
        bot = get_jorach()
        user = ctx.message.author
        try:
            raid_name = await prompt_freeform("What do you want to name the raid?\n" + \
            "(One word, alphanumeric only, e.g. `ony` or `bwl`)", user)
            raid_month = MONTHS.index(await prompt_choices("What month do you want to host the raid?", user, MONTHS)) + 1
            raid_date = await prompt_freeform("What date do you want to hold the raid (e.g. 1 through 31)", user)
            raid_time = await prompt_freeform("What time do you want to hold the raid? (Use military time, e.g. 18:30)", user)
            raid_type = await prompt_choices("What type of raid is this?", user, list(RAID_TYPE_DRAWER_MAP.keys()))
            raid_category = RAID_TYPE_DRAWER_MAP.get(raid_type, None)
            role_mention = RAID_TYPE_MENTION_ROLE_MAP.get(raid_type, None)
            if not raid_category or not role_mention:
                raise Exception("Invalid raid type.")
                return
        except Exception as e:
            await user.send("Oops! Something went wrong. {}".format(str(e)))
            return

        # remove colons because it screws up some sheets calls, heh
        raid_title = "{} - {} {}/{} @ {}".format(raid_type, raid_name, raid_month, raid_date, raid_time).replace(":", "")
        safe_raid_name = raid_name.replace(" ", "-")
        channel_name = "{}-{}-{}".format(raid_month, raid_date, raid_name)
        # If the sheet is already made for whatever reason, just get it
        try:
            worksheet = duplicate_sheet(raid_title)
        except APIError:
            worksheet = get_worksheet(raid_title)

        embed = discord.Embed()
        embed.color = discord.Color.green()
        embed.title = raid_title
        embed.description = BASE_RAID_DESCRIPTION
        embed.add_field(name="DPS", value=0)
        embed.add_field(name="Healer", value=0)
        embed.add_field(name="Tank", value=0)
        embed.url = get_worksheet_link(worksheet)

        category = await self.create_category_if_not_exists(ctx, raid_category)

        for c in category.channels:
            if c.name == channel_name:
                print("Already have a channel with this name, cancelling")
                return
        channel = await category.create_text_channel(channel_name)

        msg = await channel.send(embed=embed)
        await msg.add_reaction(SIGNUP_EMOJI)
        await channel.send("New raid signups are open! {}".format(role_mention))
        await user.send("Successfully created a raid in the {} category!".format(raid_category))
        return

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def deleteraid(self, ctx):
        """
        Deletes a raid when used in a raid signup channel (admin only)

        DEVELOPER INFO:
        :param ctx: The context of invocation for the command that sheet was ran on.
        """
        channel = ctx.channel
        # Only delete channels in the raid categories
        if channel.category.name.lower() in [v.lower() for v in RAID_TYPE_DRAWER_MAP.values()]:
            async for message in channel.history(limit=1, oldest_first=True):
                if len(message.embeds) > 0:
                    sheet_title = message.embeds[0].title
                    try:
                        delete_worksheet(sheet_title)
                    except Exception:
                        await ctx.message.author.send("Failed to delete the associated sheet: {}".format(sheet_title))
                    await channel.delete()

    async def create_category_if_not_exists(self, ctx, category_name):
        guild = ctx.message.guild
        categories = guild.categories
        category = None
        # Create the category
        for c in categories:
            if c.name.lower() == category_name.lower():
                category = c
        if category == None:
            category = await guild.create_category(category_name)
        return category

    async def _post_add_identity_embed(self, channel):
        embed = discord.Embed()
        embed.color = discord.Color.green()
        embed.title = ADD_IDENTITY_EMBED_TITLE
        embed.description = ADD_IDENTITY_DESCRIPTION

        msg = await channel.send(embed=embed)
        await msg.add_reaction(INTERACT_EMOJI)

    async def _post_edit_identity_embed(self, channel):
        embed = discord.Embed()
        embed.color = discord.Color.gold()
        embed.title = EDIT_IDENTITY_EMBED_TITLE
        embed.description = EDIT_IDENTITY_DESCRIPTION

        msg = await channel.send(embed=embed)
        await msg.add_reaction(INTERACT_EMOJI)

    async def _post_remove_identity_embed(self, channel):
        embed = discord.Embed()
        embed.color = discord.Color.red()
        embed.title = REMOVE_IDENTITY_EMBED_TITLE
        embed.description = REMOVE_IDENTITY_DESCRIPTION

        msg = await channel.send(embed=embed)
        await msg.add_reaction(INTERACT_EMOJI)