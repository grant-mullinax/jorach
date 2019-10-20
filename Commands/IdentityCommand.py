from discord.ext import commands

from schema.classes import *
from schema.roles import *
from sheets.client import *


class IdentityCommand(commands.Cog):
    """
    `IdentityCommand` is a class that allows users to create a profile for
    themselves so that they can register for raids.
    """

    @commands.command(name="identity", description="Registers your identity with the bot on the spreadsheet")
    async def run_command(self, ctx, name: str, wow_class: str, role: str):
        """
        Registers the user in the spreadsheet provided all info is correct. Otherwise, informs the user that this
        command failed due to their syntax.

        :param ctx: The context of invocation for the command that sheet was ran on.
        :param params: An array of 3 objects in this order: name, class, and role
        """
        classes = get_all_classes()
        roles = get_all_roles()

        if wow_class.lower() not in classes:
            await ctx.send("Invalid class name.")
            return

        if role.lower() not in roles:
            await ctx.send("Invalid role, valid roles are %s" + ", ".join(roles))
            return

        identity_worksheet = get_identity_worksheet()

        discord_ids = col_values(identity_worksheet, 1)
        author_hash = str(hash(ctx.author))

        if author_hash in discord_ids:
            delete_row(identity_worksheet, discord_ids.index(author_hash) + 1)  # sheets is indexed starting at 1

        append_row(identity_worksheet,
            [author_hash, str(ctx.author), name.lower(), wow_class.lower(), role.lower()])
        await ctx.send("Your identity has been recorded.")
        return
