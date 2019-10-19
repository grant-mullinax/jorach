from discord.ext import commands

from Commands.SafeOAuthBasedCommand import SafeOAuthBasedCommand


class RolesCommand(SafeOAuthBasedCommand):
    """
    `RolesCommand` is a class conforming to `SafeOAuthBasedCommand` that allows users to request to available roles
    to sign up for in `IdentityCommand`.

    This command will likely be removed in the future as we move to emote-based signups.
    """

    def __init__(self, list_available_roles):
        """
        Initializes a `RolesCommand` with the provided roles.

        :param list_available_roles: The roles that are available for users to select
        """
        self.__list_available_roles = list_available_roles
        return

    @commands.command(name="roles", description="Lists all available roles")
    async def execute_sheet_command(self, ctx):
        await self.execute(ctx=ctx, params=None)
        return

    async def run_command(self, ctx, params):
        """
        Informs the user on what roles are available for selection.

        :param ctx: The context of invocation for the command that sheet was ran on.
        :param params: No parameters are used.
        """
        await ctx.send("Valid roles are: %s" % ", ".join(self.__list_available_roles))
        return
