from datetime import date, datetime, timedelta

from pytz import timezone
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
        # 2020-02-09 8AM PST is a sample Onyxia reset time.
        seed_time = "2020-02-09 08:00:00"
        seed_date = datetime.strptime(seed_time, "%Y-%m-%d %H:%M:%S")

        # localize helps us deal with DST. Not sure if I actually need to account for this.
        tz = timezone("US/Pacific")
        seed_date = tz.localize(seed_date)
        today = datetime.now().astimezone(tz)
        onys_since = (today-seed_date).days // 5
        ony_time = seed_date + timedelta(days=5*onys_since+5)
        time_until = ony_time-today
        await ctx.send("The next Onyxia reset is in `{}d{}h{}m` on `{}`".format(
            time_until.days,
            time_until.seconds // 3600,
            (time_until.seconds % 3600) // 60,
            ony_time.strftime("%A %b %d"),
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
