from menus.embed import EmbedMenu
from providers.jorach_bot import prompt_choices
from schema.constants import *
from sheets.client import *


class RemoveIdentityMenu(EmbedMenu):
    async def check_message(self, channel, msg, user) -> bool:
        """
        Returns true if the message embed title is the add identity title
        """
        return channel.category.name == START_HERE_CATEGORY \
            and msg.embeds[0].title == REMOVE_IDENTITY_EMBED_TITLE

    async def handle_emoji(self, emoji, channel, msg, user, guild, member):
        await msg.remove_reaction(emoji, user)
        identity_worksheet = get_identity_worksheet()
        member_id = str(member.id)

        user_rows = get_rows_with_value_in_column(identity_worksheet,
                                                  column_index=1, value_to_find=member_id)

        if not user_rows:
            raise Exception(
                "Unable to delete identity: You do not have any profiles set up.")

        character_names = [row_values(identity_worksheet, row)[
            2].lower() for row in user_rows]
        name = await prompt_choices("Which character would you like to delete?", user, character_names)

        # The user has other profiles; make sure a character with the name exists!
        matching_rows = get_rows_with_value_in_column(identity_worksheet, column_index=3,
                                                      value_to_find=name.lower(), list_search_rows=user_rows)
        if len(matching_rows) > 1:
            raise Exception(
                "Unable to edit identity: More than one record exists for identity named `{}`".format(name))
            return

        delete_row(identity_worksheet, matching_rows[0])
        await user.send("Identity with name `{}` deleted successfully.".format(name))
        return
