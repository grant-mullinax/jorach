import discord
from discord.ext import commands
from datetime import datetime

from sheets.client import *


SIGNUP_EMOJI = "☑"
CLOSE_SIGNUP_EMOJI ="🛑"
BASE_RAID_DESCRIPTION = "React with your class or spec to register for the raid! Raid times are in server time (PST/PDT)"


class Management(commands.Cog):

    """
    `Management` is a class that allows admin users to create raids for users
    """

    @commands.command()
    async def startraid(self, ctx, raid_name: str, raid_month: int, raid_date: int, raid_hour: str, raid_min: str):
        """
        Starts a new raid with a given name on a given date.

        Example: TODO

        DEVELOPER INFO:
        :param raid_name:
        :param raid_month:
        :param raid_date:
        :param raid_hour:
        :param raid_min:
        :param ctx: The context of invocation for the command that sheet was ran on.
        """
        # remove colons because it screws up some sheets calls, heh
        raid_title = "Raid - {} {}/{} @ {}{}".format(raid_name, raid_month, raid_date, raid_hour, raid_min)
        safe_raid_name = raid_name.replace(" ", "-")
        channel_name = "{}-{}-{}".format(raid_title, raid_month, raid_date)
        # If the sheet is already made for whatever reason, just get it
        try:
            worksheet = duplicate_sheet(raid_title)
        except APIError:
            worksheet = get_worksheet(raid_title)

        raid_datetime = datetime(datetime.now().year, int(raid_month), int(raid_date), int(raid_hour), int(raid_min))
        update_cell(worksheet, 1, 26, raid_datetime.isoformat())

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
            if c.name.lower() == "raids":
                category = c
        if category == None:
            category = await guild.create_category("Raids")

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
