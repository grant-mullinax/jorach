from discord.ext import commands

from schema.classes import *
from schema.roles import *
from Commands.SafeOAuthBasedCommand import SafeOAuthBasedCommand


class IdentityCommand(SafeOAuthBasedCommand):
    """
    `IdentityCommand` is a class conforming to `SafeOAuthBasedCommand` that allows users to create a profile for
    themselves so that they can register for raids.
    """

    def __init__(self, identity_worksheet):
        """
        Initializes an `IdentityCommand` with the provided classes and roles that are available.

        :param identity_worksheet: The worksheet where user identities should be stored to
        """
        self.__identity_worksheet = identity_worksheet
        return

    @commands.command(name="identity", description="Registers your identity with the bot on the spreadsheet")
    async def execute_sheet_command(self, ctx, name: str, wow_class: str, role: str):
        await self.execute(ctx=ctx, params=[name, wow_class, role])
        return

    async def run_command(self, ctx, params):
        """
        Registers the user in the spreadsheet provided all info is correct. Otherwise, informs the user that this
        command failed due to their syntax.

        :param ctx: The context of invocation for the command that sheet was ran on.
        :param params: An array of 3 objects in this order: name, class, and role
        """
        name, wow_class, role = params[:3]
        classes = get_all_classes()
        roles = get_all_roles()

        if wow_class.lower() not in classes:
            await ctx.send("Invalid class name.")
            return

        if role.lower() not in roles:
            await ctx.send("Invalid role, valid roles are %s" + ", ".join(roles))
            return

        discord_ids = self.__identity_worksheet.col_values(1)
        author_hash = str(hash(ctx.author))

        if author_hash in discord_ids:
            self.__identity_worksheet.delete_row(discord_ids.index(author_hash) + 1)  # sheets is indexed starting at 1

        self.__identity_worksheet.append_row(
            [author_hash, str(ctx.author), name.lower(), wow_class.lower(), role.lower()])
        await ctx.send("Your identity has been recorded.")
        return
