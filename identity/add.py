from discord.utils import get
from menus.embed import EmbedMenu
from providers.jorach_bot import prompt_choices, prompt_freeform
from schema.classes import *
from schema.constants import *
from sheets.client import *


class AddIdentityMenu(EmbedMenu):
    async def check_message(self, channel, msg, user) -> bool:
        """
        Returns true if the message embed title is the add identity title
        """
        return channel.category.name == START_HERE_CATEGORY \
            and msg.embeds[0].title == ADD_IDENTITY_EMBED_TITLE

    async def handle_emoji(self, emoji, channel, msg, user, guild, member):
        """
        Set up a user identity from info parsed out of a reaction to a message
        """
        await msg.remove_reaction(emoji, user)
        member_id = str(member.id)

        # Gather and validate user info.
        name = await prompt_freeform('What is your character name?', user)
        name = name.title()
        # Raise if a duplicate name is found
        _find_duplicate_name(member_id, name)
        wow_class = await prompt_choices('What is your class?', user, get_all_classes())
        wow_role = await prompt_choices('What is your role?', user, get_class_roles(wow_class))

        # Attempt to attach both a class role and the 'Raider' role by default.
        # The 'Ravenguard' role MUST be added by an admin manually because we have no way of
        # programmatically verifying it.
        is_alt = await _add_roles(wow_class, guild, member)

        if not is_alt:
            await _add_nick(member, name)

        # User does not have a character with the same name; class and role valid. Can register a new profile
        append_row(identity_worksheet, [member_id, str(
            user), name.lower(), wow_class.lower(), wow_role.lower()])
        await user.send('{} registered successfully.'.format(name))


async def _add_roles(wow_class, guild, member):
    """
    Create the appropriate roles if necessary and attach them to the member
    """
    role_names = [str(role) for role in member.roles]
    class_role_names = CLASS_ROLE_MAP.keys()
    is_alt = len(set.intersection(set(role_names), set(class_role_names))) >= 1
    if is_alt:
        wow_class = '{}-Alt'.format(wow_class)
    class_role = get(guild.roles, name=wow_class)
    roles_to_add = [class_role]
    ravenguard_role = get(guild.roles, name=RAVENGUARD_ROLE_NAME)
    raider_role = get(guild.roles, name=RAIDER_ROLE_NAME)
    if ravenguard_role not in member.roles and raider_role not in member.roles:
        roles_to_add.append(raider_role)
    await member.add_roles(*roles_to_add)
    return is_alt


async def _add_nick(member, nickname):
    if not member.nick:
        try:
            await member.edit(nick=nickname)
        except:
            # This can fail if the member is too high up on the hierarchy (the bot can't change the nickname
            # of a server owner). Just let it slide for now.
            raise Exception(
                'Could not change nickname for {}'.format(member.name))


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
            raise Exception(
                'Unable to add profile: You already have a character named `{}`'.format(name))
