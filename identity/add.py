from providers.jorach_bot import prompt_choices, prompt_freeform
from schema.classes import get_all_classes, get_class_roles
from schema.constants import *
from sheets.client import *


def is_bot_add_identity_msg(bot, msg, channel, user):
    """
    Returns true if the given message was posted by the bot,
    the user reacting is NOT the bot, AND the message embed title is the add identity title
    """
    return (msg.author.id == bot.user.id
            and user.id != bot.user.id
            and channel.category.name == START_HERE_CATEGORY
            and len(msg.embeds) > 0
            and msg.embeds[0].title == ADD_IDENTITY_EMBED_TITLE
    )


async def add_identity(bot, channel, msg, user, guild, member, payload):
    """
    Set up a user identity from info parsed out of a reaction to a message
    """
    member_id = str(member.id)

    # Gather and validate user info.
    try:
        name = await prompt_freeform("What is your character name?", user)
        _find_duplicate_name(member_id, name)
        wow_class = await prompt_choices("What is your class?", user, get_all_classes())
        wow_role = await prompt_choices("What is your role?", user, get_class_roles(wow_class))
    except Exception as e:
        user.send("Oops, something went wrong: {}".format(str(e)))
        return

    # Attempt to attach both a class role and the "Raider" role by default.
    # The "Ravenguard" role MUST be added by an admin manually because we have no way of
    # programmatically verifying it.
    await _add_roles(wow_class, guild, member)
    await _add_nick(member, name)

    # User does not have a character with the same name; class and role valid. Can register a new profile
    append_row(identity_worksheet, [member_id, str(user), name.lower(), wow_class.lower(), wow_role.lower()])
    await user.send("\"%s\" registered successfully." % name)


async def _add_roles(wow_class, guild, member):
    """
    Create the appropriate roles if necessary and attach them to the member
    """
    raider_role = None
    class_role = None
    for role in guild.roles:
        if str(role).lower() == RAIDER_ROLE_NAME:
            raider_role = role
        elif str(role).lower() == wow_class.lower():
            class_role = role
        if class_role and raider_role:
            break
    if not raider_role:
        raider_role = await guild.create_role(name=RAIDER_ROLE_NAME)
    if not class_role:
        class_role = await guild.create_role(name=wow_class)
    await member.add_roles(raider_role, class_role)


async def _add_nick(member, nickname):
    if not member.nick:
        try:
            await member.edit(nick=nickname)
        except:
            # This can fail if the member is too high up on the hierarchy (the bot can't change the nickname
            # of a server owner). Just let it slide for now.
            print("Could not change nickname for {}".format(member.name))


def _find_duplicate_name(member_id: str, name: str):
    """
    Search for a duplicate name registered under the given member ID.
    Raise an Exception if there's a problem. Otherwise do nothing.
    """
    identity_worksheet = get_identity_worksheet()

    rows_for_user_with_id = get_rows_with_value_in_column(identity_worksheet, column_index=1,
         value_to_find=member_id)

    if rows_for_user_with_id:
        # The user has other profiles; make sure they don't duplicate an entry with the same character name
        rows_with_name_for_user_with_id = get_rows_with_value_in_column(identity_worksheet,
            column_index=3, value_to_find=name.lower(), list_search_rows=rows_for_user_with_id)

        if rows_with_name_for_user_with_id:
            # Uh oh.. the user already registered a character with the same name! Tell them they STUPID.
            raise Exception("Unable to add profile: You already have a character named `{}`".format(name))