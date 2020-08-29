from menus.embed import EmbedMenu
from providers.jorach_bot import prompt_choices, prompt_freeform
from schema.classes import get_all_classes, get_class_roles
from schema.constants import *
from sheets.client import *


class EditIdentityMenu(EmbedMenu):
    async def check_message(self, channel, msg, user) -> bool:
        """
        Returns true if the message embed title is the add identity title
        """
        return (channel.name == IDENTITY_MANAGEMENT_CHANNEL
                and channel.category.name == START_HERE_CATEGORY
                and msg.embeds[0].title == EDIT_IDENTITY_EMBED_TITLE
                )

    async def handle_emoji(self, emoji, channel, msg, user, guild, member):
        """
        Edits your identity as set up with the bot.
        """
        await msg.remove_reaction(emoji, user)
        identity_worksheet = get_identity_worksheet()
        member_id = str(member.id)

        user_rows = get_rows_with_value_in_column(identity_worksheet,
                                                  column_index=1, value_to_find=member_id)

        if not user_rows:
            raise Exception(
                "Unable to edit identity: Could not find any identities to edit.")

        character_names = [row_values(identity_worksheet, row)[
            2].title() for row in user_rows]
        name = await prompt_choices("Which identity would you like to edit?", user, character_names)
        # The user has other profiles; make sure a character with the name exists!
        named_rows = get_rows_with_value_in_column(identity_worksheet, column_index=3,
                                                   value_to_find=name.lower(), list_search_rows=user_rows)
        data = row_values(identity_worksheet, named_rows[0])
        wow_class = data[3]
        wow_role = await prompt_choices("What is your role?", user, get_class_roles(wow_class))
        for r in named_rows:
            delete_row(identity_worksheet, r)
        append_row(identity_worksheet, [member_id, str(
            member), name.lower(), wow_class.lower(), wow_role.lower()])
        await user.send("Your identity was updated successfully!")
