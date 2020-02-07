import discord
from discord.ext import commands

from sheets.client import *


SIGNUP_EMOJI = "☑"
CLOSE_SIGNUP_EMOJI ="🛑"
BASE_RAID_DESCRIPTION = \
    ("React with %s to register for this raid! Raid times are in server time (PST/PDT)" % SIGNUP_EMOJI) \
    + "\n\nNote that is is your responsibility to confirm that you have been signed up properly. If you run into an " \
    + "issue while signing up, please contact a moderator."
RAID_DRAWER_CATEGORY = "raids"

class Management(commands.Cog):

    """
    `Management` is a class that allows admin users to create raids for users
    """

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def startraid(self, ctx, raid_name: str, raid_month: int, raid_date: int, raid_time: str):
        """
        Starts a new raid with a given name on a given date.

        Example: TODO

        DEVELOPER INFO:
        :param raid_name:
        :param raid_month:
        :param raid_date:
        :param raid_time:
        :param ctx: The context of invocation for the command that sheet was ran on.
        """
        # remove colons because it screws up some sheets calls, heh
        raid_title = "Raid - {} {}/{} @ {}".format(raid_name, raid_month, raid_date, raid_time).replace(":", "")
        safe_raid_name = raid_name.replace(" ", "-")
        channel_name = "{}-{}-{}".format(raid_title, raid_month, raid_date)
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

        guild = ctx.message.guild
        categories = guild.categories
        category = None
        for c in categories:
            if c.name.lower() == RAID_DRAWER_CATEGORY:
                category = c
        if category == None:
            category = await guild.create_category(RAID_DRAWER_CATEGORY)

        safe_raid_name = raid_name.replace(" ", "-")
        channel_name = "{}-{}-{}".format(safe_raid_name, raid_month, raid_date)
        for c in category.channels:
            if c.name == channel_name:
                print("Already have a channel with this name, cancelling")
                return
        channel = await category.create_text_channel(channel_name)

        msg = await channel.send(embed=embed)
        await msg.add_reaction(SIGNUP_EMOJI)
        return

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def deleteraid(self, ctx):
        channel = ctx.channel
        # Only delete channels in the `raids` category
        if channel.category.name.lower() == RAID_DRAWER_CATEGORY:
            async for message in channel.history(limit=1, oldest_first=True):
                if len(message.embeds) > 0 and message.embeds[0].title.startswith("Raid -"):
                    sheet_title = message.embeds[0].title
                    try:
                        delete_worksheet(sheet_title)
                    except Exception:
                        print("Can't find the sheet {}".format(sheet_title))
                    await channel.delete()