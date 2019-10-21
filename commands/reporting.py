from discord.ext import commands

from schema.classes import *
from schema.roles import *
from sheets.client import *

from datetime import datetime


class Reporting(commands.Cog):
    """
    `Reporting` is a class that contains a variety of commands that allow users to interact with the
    raid registration and signup system.
    """

    @commands.command()
    async def identity(self, ctx, name: str, wow_class: str, role: str):
        """
        Registers your character identity with the bot.

        Example: "!identity Jorach Rogue DPS"

        DEVELOPER INFO:
        :param ctx: The context of invocation for the command that identity was ran on.
        :param name: in-game character name
        :param wow_class: character class
        :param role: role of the character
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

    @commands.command()
    async def register(self, ctx, raid_name: str):
        """
        Used to register for a raid with an input name.

        Example: "!register mc1"

        DEVELOPER INFO:
        :param ctx: The context of invocation for the command that register was ran on.
        :param raid_name: the name of the raid to register for
        """

        discord_ids = col_values(identity_worksheet, 1)
        author_hash = str(hash(ctx.author))

        if author_hash not in discord_ids:
            await ctx.send("Your identity has not been recorded! Please use the !identity command")
            return

        raid_name_lower = raid_name.lower()
        raid_names = [ws.title for ws in get_raid_worksheets()]
        if raid_name_lower not in raid_names:
            await ctx.send("That is not a valid raid! Please use !raids to see what raids are available.")
            return

        raid_worksheet = get_worksheet(raid_name_lower)
        identity_values = row_values(identity_worksheet, discord_ids.index(author_hash) + 1)

        name, wow_class, role = identity_values[2:5]
        names = col_values(raid_worksheet, 1)

        if name in names:
            await ctx.send("You have already signed up for this raid!")
            return

        # hacky workaround for append row not working here
        insert_row(raid_worksheet, [name, wow_class, role, str(datetime.now())], len(names) + 1)
        await ctx.send("Your availability has been noted for the upcoming raid.")

    @commands.command()
    async def onyattunement(self, ctx, attuned: bool):
        """
        Used to set Onyxia attunement status to your identity.

        Example: "!onyattunement Yes"

        DEVELOPER INFO:
        :param ctx: The context of invocation for the command that sheet was ran on.
        :param attuned: whether or not the user is attuned.
        """
        discord_ids = col_values(get_identity_worksheet(), 1)
        author_hash = str(hash(ctx.author))

        if author_hash not in discord_ids:
            await ctx.send("Your identity has not been recorded! Please use the !identity command")
            return

        update_cell(identity_worksheet, discord_ids.index(author_hash) + 1, 6, str(attuned))
        await ctx.send("Your attunement has been recorded.")
        return
