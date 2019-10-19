from discord.ext import commands

from Commands.SafeOAuthBasedCommand import SafeOAuthBasedCommand


class SheetCommand(SafeOAuthBasedCommand):
    """
    `SheetCommand` is a class conforming to SafeOAuthBasedCommand that allows users to request to see the sheet
    where raid info is being recorded. This command can be ran by users via `[prefix]sheet`.
    """

    def __init__(self, spreadsheet_id):
        """
        Initializes a SheetCommand with the provided spreadsheet id. This ID is used to later link the ID if a user
        needs wants to access the sheet.

        :param spreadsheet_id: The ID of the sheet that should be linked.
        """
        self.__spreadsheet_name = spreadsheet_id
        return

    @commands.command(name="sheet", description="Provides a link to the registry spreadsheet")
    async def execute_sheet_command(self, ctx):
        await self.execute(ctx=ctx, params=None)
        return

    async def run_command(self, ctx, params):
        """
        Sends a message to the contextual channel with the spreadsheet where info is being recorded.

        :param ctx: The context of invocation for the command that sheet was ran on.
        :param params: No parameters are used.
        """
        await ctx.send("See the spreadsheet at:\n https://docs.google.com/spreadsheets/d/%s" % self.__spreadsheet_name)
        return

