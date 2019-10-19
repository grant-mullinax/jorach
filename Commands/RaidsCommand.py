from discord.ext import commands

from Commands.SafeOAuthBasedCommand import SafeOAuthBasedCommand


class RaidsCommand(SafeOAuthBasedCommand):
    """
    `RaidsCommand` is a class conforming to `SafeOAuthBasedCommand` that allows users to view available raids that can
    be signed up for.

    This command will likely be removed in the future as we move to emote-based signups.
    """

    def __init__(self, spreadsheet, excluded_sheet_names):
        """
        Initializes a `RaidsCommand` object with the gspread spreadsheet object. This object is assumed to be valid.

        :param spreadsheet: A gspread spreadsheet object
        :param excluded_sheet_names: A list of strings that includes the names of all sheets on the provided spreadsheet
                                     to not list.
        """
        self.__spreadsheet = spreadsheet
        self.__excluded_sheet_names = excluded_sheet_names
        return

    @commands.command(name="raids", description="Lists all available raids")
    async def execute_sheet_command(self, ctx):
        await self.execute(ctx=ctx, params=None)
        return

    async def run_command(self, ctx, params):
        """
        Sends a message informing the user what raids are currently available.

        :param ctx: The context of invocation for the command that sheet was ran on.
        :param params: No parameters are used.
        """
        worksheets = self.__spreadsheet.worksheets()  # probably can consolidate this with the register command
        sheet_names = list(map(lambda ws: ws.title, worksheets))
        raid_names = [sheet_name for sheet_name in sheet_names if sheet_name not in self.__excluded_sheet_names]

        if not raid_names:
            await ctx.send("There are no raids scheduled right now.")
        else:
            await ctx.send("Available raids are:\n - %s" % ("\n - ".join(raid_names)))
        return
