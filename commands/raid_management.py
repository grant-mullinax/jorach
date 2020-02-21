from datetime import datetime

import discord
from discord.ext import commands
from pytz import timezone

from providers.jorach_bot import *
from schema.constants import *
from schema.util import find_by_id
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
        welcome_category = await self._create_category_if_not_exists(ctx, START_HERE_CATEGORY)

        await self._setup_message_controls(welcome_category)
        voice_category = await self._create_category_if_not_exists(ctx, "voice channels")
        await self._setup_raid_voice(voice_category)

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
            raid_date = int(await prompt_freeform("What date do you want to hold the raid (e.g. 1 through 31)", user))
            today = timezone("US/Pacific").localize(datetime.now())
            year = today.year
            # Assume we are in the year ahead if given a date that is "less than" today
            if raid_month < today.month or (raid_month == today.month and today.day > raid_date):
                year += 1
            t = datetime(year, raid_month, raid_date)
            raid_day = datetime.strftime(t, "%a").lower()
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
        raid_title = "{} - {} {} {}/{} @ {}".format(raid_type, raid_name.title(),
            raid_day.title(), raid_month, raid_date, raid_time).replace(":", "")
        safe_raid_name = raid_name.replace(" ", "-")
        channel_name = "{}-{}-{}-{}".format(raid_month, raid_date, raid_day, raid_name)
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

        category = await self._create_category_if_not_exists(ctx, raid_category)
        channel = find_by_id(category.channels, channel_name)
        if channel:
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

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def lcstart(self, ctx, raid_type):
        """
        Start a loot council session. !lcstart (rg1 || rg2)

        :param raid_type: Raid type, either RG1 or RG2
        """
        try:
            k = raid_type.upper()
            await self._channel_move_helper(ctx,
                RAID_TYPE_RAID_CHANNEL_MAP.get(k, None), RAID_TYPE_LC_CHANNEL_MAP.get(k, None))
        except:
            pass

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def lcend(self, ctx, raid_type):
        """
        Start a loot council session. !lcstart (rg1 || rg2)

        :param raid_type: Raid type, either RG1 or RG2
        """
        try:
            k = raid_type.upper()
            await self._channel_move_helper(ctx,
                RAID_TYPE_LC_CHANNEL_MAP.get(k, None), RAID_TYPE_RAID_CHANNEL_MAP.get(k, None))
        except:
            pass

    async def _channel_move_helper(self, ctx, src_channel_name, dest_channel_name):
        if not src_channel_name or not dest_channel_name:
            await ctx.message.author.send("Invalid raid type, please specify any of {}".format(
                str(list(RAID_TYPE_RAID_CHANNEL_MAP.keys())).replace("'", "")))
            return
        guild = ctx.message.guild
        category = find_by_id(guild.categories, "voice channels")
        if not category:
            await ctx.message.author.send("Couldn't find the loot council voice channel")
            return
        channels = category.voice_channels
        src_channel = find_by_id(category.voice_channels, src_channel_name)
        dest_channel = find_by_id(category.voice_channels, dest_channel_name)
        if not src_channel or not dest_channel:
            await ctx.message.author.send("Couldn't find the loot council voice channel")
            return
        role = find_by_id(guild.roles, LC_ROLE)
        if not role:
            await ctx.message.author.send("Could not find loot council role: {}".format(LC_ROLE))
            return
        for member in src_channel.members:
            if role in member.roles:
                await member.move_to(dest_channel)

    async def _create_category_if_not_exists(self, ctx, category_name):
        guild = ctx.message.guild
        category = find_by_id(guild.categories, category_name.lower())
        if category == None:
            category = await guild.create_category(category_name)
        return category

    async def _create_channel_if_not_exists(self, category, channel_name):
        channel = find_by_id(category.voice_channels, channel_name.lower())
        if channel == None:
            channel = await category.create_voice_channel(channel_name)
        return channel

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

    async def _setup_message_controls(self, category):
        # Do nothing if the channel is already made
        for c in category.channels:
            if c.name == START_HERE_CHANNEL:
                return

        channel = await category.create_text_channel(START_HERE_CHANNEL)

        await self._post_add_identity_embed(channel)
        await self._post_edit_identity_embed(channel)
        await self._post_remove_identity_embed(channel)


    async def _setup_raid_voice(self, category):
        for channel_name in [y for x in [
            list(RAID_TYPE_LC_CHANNEL_MAP.values()),
            list(RAID_TYPE_RAID_CHANNEL_MAP.values())] for y in x]:
            await self._create_channel_if_not_exists(category, channel_name)
