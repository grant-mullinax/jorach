from discord.ext import commands

from Commands.SafeOAuthBasedCommand import SafeOAuthBasedCommand


class OnyAttunementCommand(SafeOAuthBasedCommand):
    """
    `OnyAttunementCommand` is a class conforming to `SafeOAuthBasedCommand` that allows users to set their Ony attunement
    status.

    This command will likely be reworked in the future as we move to emote-based signups.
    """

    def __init__(self, identity_worksheet):
        """
        Initializes an `OnyAttunementCommand` with the provided worksheet that provides user identities.

        :param identity_worksheet: The worksheet where user identities are stored
        """
        self.__identity_worksheet = identity_worksheet
        return

    @commands.command(name="onyattunement", description="Sets whether or not you are ony attuned")
    async def execute_sheet_command(self, ctx, attuned: bool):
        await self.execute(ctx=ctx, params=[attuned])
        return

    async def run_command(self, ctx, params):
        """
        Sets the attunement status of the user provided that they have a valid identity registered. Otherwise, tells the
        user how to set their identity p.

        :param ctx: The context of invocation for the command that sheet was ran on.
        :param params: An array of 1 object: whether or not the user is attuned.
        """
        attuned = params[0]

        discord_ids = self.__identity_worksheet.col_values(1)
        author_hash = str(hash(ctx.author))

        if author_hash not in discord_ids:
            await ctx.send("Your identity has not been recorded! Please use the !identity command")
            return

        self.__identity_worksheet.update_cell(discord_ids.index(author_hash) + 1, 6, str(attuned))
        await ctx.send("Your attunement has been recorded.")
        return
