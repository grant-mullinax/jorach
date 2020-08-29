from discord.utils import get
from menus.embed import EmbedMenu
from providers.jorach_bot import prompt_choices, prompt_freeform
from schema.classes import *
from schema.constants import *
from sheets.client import *


class MainClassMenu(EmbedMenu):
    async def check_message(self, channel, msg, user) -> bool:
        """
        Returns true if the message embed title is the class picker title
        """
        return channel.category.name == START_HERE_CATEGORY \
            and msg.embeds[0].title == SELECT_MAIN_TITLE

    async def handle_emoji(self, emoji, channel, msg, user, guild, member):
        """
        Set the user's main role, remove all old roles, convert existing other main roles into their alt counterparts.
        """
        await msg.remove_reaction(emoji, user)
        if emoji.id in CLASS_EMOTE_MAP.keys():

            member_id = str(member.id)
            # Raise if a duplicate name is found
            main_role_name = CLASS_EMOTE_MAP.get(emoji.id, None)

            await _manage_roles(main_role_name, guild, member)

            await user.send('Main class changed to {}'.format(main_role_name))


async def _manage_roles(main_role_name, guild, member):
    class_roles = CLASS_ROLE_MAP.keys()
    main_role = get(guild.roles, name=main_role_name)
    roles_to_add = [main_role]
    roles_to_remove = []
    for role in member.roles:
        # Accumulate all of the main roles to be converted from main to alt
        if role == main_role:
            roles_to_add.remove(role)
            old_alt_role = get(member.roles, name='{}-Alt'.format(str(role)))
            if old_alt_role:
                roles_to_remove.append(old_alt_role)
        elif str(role) in class_roles:
            roles_to_remove.append(role)
            alt_role = get(guild.roles, name='{}-Alt'.format(str(role)))
            roles_to_add.append(alt_role)

    await member.remove_roles(*roles_to_remove)
    await member.add_roles(*roles_to_add)
