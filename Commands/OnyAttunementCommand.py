from discord.ext import commands

from sheets.client import *



class OnyAttunementCommand(commands.Cog):
    """
    `OnyAttunementCommand` is a class that allows users to set their Ony attunement
    status.

    This command will likely be reworked in the future as we move to emote-based signups.
    """

    @commands.command(name="onyattunement", description="Sets whether or not you are ony attuned")
    async def run_command(self, ctx, attuned: bool):
        """
        Sets the attunement status of the user provided that they have a valid identity registered. Otherwise, tells the
        user how to set their identity p.

        :param ctx: The context of invocation for the command that sheet was ran on.
        :param bool: whether or not the user is attuned.
        """
        identity_worksheet = get_identity_worksheet()
        discord_ids = col_values(identity_worksheet, 1)
        author_hash = str(hash(ctx.author))

        if author_hash not in discord_ids:
            await ctx.send("Your identity has not been recorded! Please use the !identity command")
            return

        update_cell(identity_worksheet, discord_ids.index(author_hash) + 1, 6, str(attuned))
        await ctx.send("Your attunement has been recorded.")
        return
