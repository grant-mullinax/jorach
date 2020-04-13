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
        await self._raid_reset_timer(ctx, 'Onyxia', '2020-02-09 08:00:00', 5)

    @commands.command()
    async def zg(self, ctx):
        """
        Shows when the next ZG reset is.

        DEVELOPER INFO:
        :param ctx: The context of invocation
        :param params: No parameters are used.
        """
        await self._raid_reset_timer(ctx, "Zul'Gurub", '2020-04-13 08:00:00', 3)

    @commands.command()
    async def sheet(self, ctx):
        """
        Links the current raid signup sheet.

        DEVELOPER INFO:
        :param ctx: The context of invocation for the command that sheet was ran on.
        """
        await ctx.send("See the spreadsheet at:\n %s" % get_spreadsheet_link())
        return

    async def _raid_reset_timer(self, ctx, raid_name, seed_time, deltadays):
        """
        :param ctx: The context of invocation for the command that sheet was ran on.
        :param raid_name: The name of the raid to track, e.g. Onyxia, ZG
        :param seed_time: Datetime string "%Y-%m-%d %H:%M:%S" for a reference reset time in US/Pacific time.
        :param deltadays: Number of days after which the raid should reset (Onyxia = 5)
        """
        seed_date = datetime.strptime(seed_time, "%Y-%m-%d %H:%M:%S")
        # localize helps us deal with DST. Not sure if I actually need to account for this.
        tz = timezone("US/Pacific")
        seed_date = tz.localize(seed_date)
        today = datetime.now().astimezone(tz)
        raids_since = (today-seed_date).days // deltadays
        raid_time = seed_date + timedelta(days=deltadays*raids_since+deltadays)
        time_until = raid_time-today
        await ctx.send("The next {} reset is in `{}d {}h {}m` on `{}`".format(
            raid_name,
            time_until.days,
            time_until.seconds // 3600,
            (time_until.seconds % 3600) // 60,
            raid_time.strftime("%A %b %d"),
        ))