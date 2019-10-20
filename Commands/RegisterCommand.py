from datetime import datetime
from discord.ext import commands

from sheets.client import *


class RegisterCommand(commands.Cog):
    """
    `RegisterCommand` is a class that allows users to register for raids.

    This command will likely be reworked in the future as we move to emote-based signups.
    """

    @commands.command(name="register", description="Signs you up for a given raid")
    async def run_command(self, ctx, raid_name: str):
        """
        Registers the user in the spreadsheet provided that they have identification and that they specified a valid
        raid. Informs them if any of these assumptions is incorrect.

        :param ctx: The context of invocation for the command that sheet was ran on.
        :param raid_name: the name of the raid to register for
        """
        await register_for_raid(ctx, ctx.author, raid_name)

async def register_for_raid(msg_sender, author, raid_name: str):
        raid_name_lower = raid_name.lower()
        identity_worksheet = get_identity_worksheet()
        if raid_name_lower == identity_worksheet.title.lower():
            await msg_sender.send("nice try")
            return

        discord_ids = col_values(identity_worksheet, 1)
        author_hash = str(hash(author))

        if author_hash not in discord_ids:
            await msg_sender.send("Your identity has not been recorded! Please use the !identity command")
            return

        worksheets = get_worksheets()
        raid_names = map(lambda ws: ws.title, worksheets)
        if raid_name not in raid_names:
            await msg_sender.send("That is not a valid raid! Please use !raids to see what raids are available.")
            return

        raid_worksheet = get_worksheet(raid_name)
        identity_values = row_values(identity_worksheet, discord_ids.index(author_hash) + 1)

        name, wow_class, role = identity_values[2:5]
        names = col_values(raid_worksheet, 1)

        if name in names:
            await msg_sender.send("You have already signed up for this raid!")
            return

        # hacky workaround for append row not working here
        insert_row(raid_worksheet, [name, wow_class, role, str(datetime.now())], len(names) + 1)
        await msg_sender.send("Your availability has been noted for the upcoming raid.")