from datetime import datetime
from discord.ext import commands

from Commands.SafeOAuthBasedCommand import SafeOAuthBasedCommand


class RegisterCommand(SafeOAuthBasedCommand):
    """
    `RegisterCommand` is a class conforming to `SafeOAuthBasedCommand` that allows users to register for raids.

    This command will likely be reworked in the future as we move to emote-based signups.
    """

    def __init__(self, spreadsheet, identity_worksheet):
        """
        Initializes an `RegisterCommand` with the provided classes and roles that are available.

        :param spreadsheet: The spreadsheet which contains worksheets that act as raid signup sheets
        :param identity_worksheet: The worksheet where user identities should be stored to
        """
        self.__spreadsheet = spreadsheet
        self.__identity_worksheet = identity_worksheet
        return

    @commands.command(name="register", description="Signs you up for a given raid")
    async def execute_sheet_command(self, ctx, raid: str):
        await self.execute(ctx=ctx, params=[raid])
        return

    async def run_command(self, ctx, params):
        """
        Registers the user in the spreadsheet provided that they have identification and that they specified a valid
        raid. Informs them if any of these assumptions is incorrect.

        :param ctx: The context of invocation for the command that sheet was ran on.
        :param params: An array of 1 object: the name of the raid to register for
        """
        raid_name = params[0]
        raid_name_lower = raid_name.lower()

        if raid_name_lower == self.__identity_worksheet.title.lower():
            await ctx.send("nice try")
            return

        discord_ids = self.__identity_worksheet.col_values(1)
        author_hash = str(hash(ctx.author))

        if author_hash not in discord_ids:
            await ctx.send("Your identity has not been recorded! Please use the !identity command")
            return

        worksheets = self.__spreadsheet.worksheets()
        raid_names = map(lambda ws: ws.title, worksheets)
        if raid_name_lower not in raid_names:
            await ctx.send("That is not a valid raid! Please use !raids to see what raids are available.")
            return

        raid_worksheet = self.__spreadsheet.worksheet(raid_name_lower)
        identity_values = self.__identity_worksheet.row_values(discord_ids.index(author_hash) + 1)

        name, wow_class, role = identity_values[2:5]
        names = raid_worksheet.col_values(1)

        if name in names:
            await ctx.send("You have already signed up for this raid!")
            return

        # hacky workaround for append row not working here
        raid_worksheet.insert_row([name, wow_class, role, str(datetime.now())], len(names) + 1)
        await ctx.send("Your availability has been noted for the upcoming raid.")
