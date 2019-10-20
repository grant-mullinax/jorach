from discord.ext import commands

from schema.roles import get_all_roles
from sheets.client import *


class Info(commands.Cog):
    """
    `Info` is a class that contains a variety of info-providing commands.
    """

    @commands.command(name="roles", description="Lists all available roles")
    async def roles(self, ctx, params=None):
        """
        Informs the user on what roles are available for selection.

        :param ctx: The context of invocation for the command that sheet was ran on.
        :param params: No parameters are used.
        """
        await ctx.send("Valid roles are: %s" % ", ".join(get_all_roles()))
        return

    @commands.command(name="raids", description="Lists all available raids")
    async def raids(self, ctx):
        """
        Sends a message informing the user what raids are currently available.

        :param ctx: The context of invocation for the command that sheet was ran on.
        :param params: No parameters are used.
        """
        raid_names = [ws.title for ws in get_raid_worksheets()]

        if not raid_names:
            await ctx.send("There are no raids scheduled right now.")
        else:
            await ctx.send("Available raids are:\n - %s" % ("\n - ".join(raid_names)))
        return

    @commands.command(name="sheet", description="Provides a link to the registry spreadsheet")
    async def run_command(self, ctx):
        """
        Sends a message to the contextual channel with the spreadsheet where info is being recorded.

        :param ctx: The context of invocation for the command that sheet was ran on.
        """
        await ctx.send("See the spreadsheet at:\n %s" % get_spreadsheet_link())
        return
