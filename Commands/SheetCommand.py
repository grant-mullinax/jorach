from discord.ext import commands

from sheets.client import *


class SheetCommand(commands.Cog):
    """
    `SheetCommand` is a class that allows users to request to see the sheet
    where raid info is being recorded. This command can be ran by users via `[prefix]sheet`.
    """

    @commands.command(name="sheet", description="Provides a link to the registry spreadsheet")
    async def run_command(self, ctx):
        """
        Sends a message to the contextual channel with the spreadsheet where info is being recorded.

        :param ctx: The context of invocation for the command that sheet was ran on.
        """
        await ctx.send("See the spreadsheet at:\n %s" % get_spreadsheet_link())
        return

