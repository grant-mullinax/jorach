from providers.jorach_bot import prompt_choices, prompt_freeform
from schema.classes import get_all_classes, get_class_roles
from schema.constants import *
from sheets.client import *


def is_bot_edit_identity_msg(bot, msg, channel, user):
    """
    Returns true if the given message was posted by the bot,
    the user reacting is NOT the bot, AND the message embed title is the add identity title
    """
    return (msg.author.id == bot.user.id
            and user.id != bot.user.id
            and channel.name == IDENTITY_MANAGEMENT_CHANNEL
            and channel.category.name == START_HERE_CATEGORY
            and len(msg.embeds) > 0
            and msg.embeds[0].title == EDIT_IDENTITY_EMBED_TITLE
    )


async def edit_identity(bot, channel, msg, user, guild, member, payload):
        """
        Edits your identity as set up with the bot.
        """
        identity_worksheet = get_identity_worksheet()
        member_id = str(member.id)

        user_rows = get_rows_with_value_in_column(identity_worksheet,
            column_index=1, value_to_find=member_id)

        if not user_rows:
            raise Exception("Unable to edit identity: Could not find any identities to edit.")

        character_names = [row_values(identity_worksheet, row)[2].title() for row in user_rows]
        name = await prompt_choices("Which identity would you like to edit?", user, character_names)
        wow_class = await prompt_choices("What is your class?", user, get_all_classes())
        wow_role = await prompt_choices("What is your role?", user, get_class_roles(wow_class))

        # The user has other profiles; make sure a character with the name exists!
        named_rows = get_rows_with_value_in_column(identity_worksheet, column_index=3,
            value_to_find=name.lower(), list_search_rows=user_rows)

        delete_row(identity_worksheet, named_rows[0])
        append_row(identity_worksheet, [member_id, str(member), name.lower(), wow_class.lower(), wow_role.lower()])
        await user.send("Your identity was updated successfully!")