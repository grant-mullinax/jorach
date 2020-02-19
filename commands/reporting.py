from discord.ext import commands

from schema.classes import *
from schema.roles import *
from sheets.client import *

class Reporting(commands.Cog):
    """
    `Reporting` is a class that contains a variety of commands that allow users to interact with the
    raid registration and signup system.
    """
    @commands.command(name="editidentity")
    async def edit_identity(self, ctx, name: str, wow_class: str, role: str):
        """
        Edits your identity as set up with the bot.

        Example: "!editidentity Jorach Mage Healer"

        DEVELOPER INFO:
        :param ctx: The context of invocation for the command that identity was ran on.
        :param name: in-game character name
        :param wow_class: character class
        :param role: role of the character
        """
        if not is_valid_class(wow_class):
            await ctx.author.send("Invalid class name, valid classes are {}".format(",".join(get_all_classes())))
            return

        if not is_valid_role(role):
            await ctx.author.send("Invalid role, valid roles are {}".format(", ".join(get_all_roles())))
            return

        identity_worksheet = get_identity_worksheet()
        author_id = str(ctx.author.id)

        rows_for_user_with_id = \
            get_rows_with_value_in_column(identity_worksheet, column_index=1, value_to_find=author_id)
        # quickly see if the row exists for the

        if not rows_for_user_with_id:
            await ctx.author.send("Unable to edit identity: Could not find any identities to edit.")
            return

        # The user has other profiles; make sure a character with the name exists!
        rows_with_name_for_user_with_id = \
            get_rows_with_value_in_column(identity_worksheet, column_index=3, value_to_find=name.lower(),
                                          list_search_rows=rows_for_user_with_id)
        if len(rows_with_name_for_user_with_id) == 0:
            await ctx.author.send(
                "Unable to edit identity: Could not find any identities with name \"%s\" to edit." % name)
            return
        elif len(rows_with_name_for_user_with_id) > 1:
            await ctx.author.send("Unable to edit identity: More than one record exists for identity named \"%s\"" %
                                  name)
            return

        # Delete the old record
        delete_row(identity_worksheet, rows_with_name_for_user_with_id[0])
        # Add the new one
        append_row(identity_worksheet, [author_id, str(ctx.author), name.lower(), wow_class.lower(), role.lower()])
        await ctx.author.send("Your identity was updated successfully!")
        return

    @commands.command(name="removeidentity")
    async def remove_identity(self, ctx, name: str):
        """
        Removes an identity associated to you by its name.

        Example: "!removeidentity Jorach"

        DEVELOPER INFO:
        :param ctx: The context this command was invoked in
        :param name: The name of the character to delete
        """
        identity_worksheet = get_identity_worksheet()
        author_id = str(ctx.author.id)

        rows_for_user_with_id = \
            get_rows_with_value_in_column(identity_worksheet, column_index=1, value_to_find=author_id)

        # Empty amount of rows; special error message for the user (would be caught in below loop, but i like separate
        # better)
        if not rows_for_user_with_id:
            await ctx.author.send("Unable to delete identity: You do not have any profiles set up." % name)
            return

        # The user has other profiles; make sure a character with the name exists!
        rows_with_name_for_user_with_id = \
            get_rows_with_value_in_column(identity_worksheet, column_index=3, value_to_find=name.lower(),
                                          list_search_rows=rows_for_user_with_id)
        if len(rows_with_name_for_user_with_id) == 0:
            await ctx.author.send("Unable to delete identity: Could not find a character named \"%s\"." % name)
            return
        elif len(rows_with_name_for_user_with_id) > 1:
            await ctx.author.send("Unable to edit identity: More than one record exists for identity named \"%s\"" %
                                  name)
            return

        delete_row(identity_worksheet, rows_with_name_for_user_with_id[0])
        await ctx.author.send("Identity with name \"%s\" deleted successfully." % name)
        return
