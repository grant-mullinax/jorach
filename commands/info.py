from datetime import date, datetime, timedelta

from discord.ext import commands

from schema.roles import get_all_roles
from sheets.client import *


class Info(commands.Cog):
    """
    `Info` is a class that contains a variety of info-providing commands.
    """
    @commands.command()
    async def ony(self, ctx):
        """
        Shows when the next Onyxia reset is.

        DEVELOPER INFO:
        :param ctx: The context of invocation
        :param params: No parameters are used.
        """
        seed_date = datetime.strptime("1/5/20", "%m/%d/%y")
        today = datetime.combine(date.today(), datetime.min.time())
        days_until_ony = 5 - (today - seed_date).days % 5
        onyxia_time = today + timedelta(days=days_until_ony)
        prev_ony = onyxia_time + timedelta(days=-5)
        await ctx.send("The next Onyxia reset is on {}\nThe previous reset was on {}".format(
            onyxia_time.strftime("%A %b %d"),
            prev_ony.strftime("%A %b %d"),
        ))

    @commands.command()
    async def raids(self, ctx):
        """
        Shows what raids are available.

        DEVELOPER INFO:
        :param ctx: The context of invocation for the command that sheet was ran on.
        :param params: No parameters are used.
        """
        raid_names = [ws.title for ws in get_raid_worksheets()]

        if not raid_names:
            await ctx.send("There are no raids scheduled right now.")
        else:
            await ctx.send("Available raids are:\n - %s" % ("\n - ".join(raid_names)))
        return

    @commands.command()
    async def sheet(self, ctx):
        """
        Links the current raid signup sheet.

        DEVELOPER INFO:
        :param ctx: The context of invocation for the command that sheet was ran on.
        """
        await ctx.send("See the spreadsheet at:\n %s" % get_spreadsheet_link())
        return
