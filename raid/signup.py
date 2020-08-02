from datetime import datetime

import discord

from menus.embed import EmbedMenu
from providers.jorach_bot import prompt_choices
from raid.util import is_raid_category
from schema.constants import *
from sheets.client import *


class RaidSignupMenu(EmbedMenu):
    async def check_message(self, channel, msg, user) -> bool:
        """
        Returns true if the the message is in an appropriate channel with a signup title
        """
        return is_raid_category(channel) and _is_raid_signup_title(msg.embeds[0])

    async def handle_emoji(self, emoji, channel, msg, user, guild, member):
        embed = msg.embeds[0]
        # Remove the reaction if the emoji isn't part of the raid signup process
        if str(emoji) not in [SIGNUP_EMOJI]:
            await msg.remove_reaction(emoji, user)
            return

        raid_worksheet = get_worksheet(embed.title)
        user_profile_rows = get_rows_with_value_in_column(
            identity_worksheet, 1, str(member.id))
        if not user_profile_rows:
            raise Exception('You need to register a character before you can sign '
                            + 'up for raids! See the {} channel for info'.format(IDENTITY_MANAGEMENT_CHANNEL))

        chosen_row = None
        # Set up mapping between the identity and the row
        identity_to_row_map = {}
        user_identities = []
        for row in user_profile_rows:
            # 2 is the 0-index of the name column in the identity sheet
            k = row_values(identity_worksheet, row)[2].lower()
            identity_to_row_map[k] = row
            user_identities.append(k)
        user_choice = await prompt_choices('Which character would you like to sign up with?', user, user_identities)
        chosen_row = identity_to_row_map[user_choice]

        identity_values = row_values(identity_worksheet, chosen_row)
        user_id, _, name, wow_class, role = identity_values[0:5]
        names = col_values(raid_worksheet, 1)

        insert_row(raid_worksheet, [name, wow_class, role, str(
            datetime.now()), user_id], len(names) + 1)

        await user.send('Thank you! Your attendance has been recorded successfully.')
        await _update_raid_embed(msg)


class RaidDeregisterMenu(EmbedMenu):
    async def check_message(self, channel, msg, user) -> bool:
        """
        Returns true if the the message is in an appropriate channel with a signup title
        """
        return is_raid_category(channel) and _is_raid_signup_title(msg.embeds[0])

    async def handle_emoji(self, emoji, channel, msg, user, guild, member):
        if str(emoji) == SIGNUP_EMOJI:
            embed = msg.embeds[0]
            raid_worksheet = get_worksheet(embed.title)

            user_ids = col_values(raid_worksheet, 5)
            try:
                # Try to delete by the member id
                delete_row(raid_worksheet, user_ids.index(str(member.id)) + 1)
            except ValueError:
                # TODO: Can remove this try/except block after the migration is complete.
                try:
                    # If member ID doesn't exist, it's because we're still migrating to the new schema.
                    # Delete it by the user id.
                    delete_row(raid_worksheet, user_ids.index(str(user)) + 1)
                except ValueError:
                    # Treat deletion of an ID that doesn't exist as idempotent success
                    pass
            await _update_raid_embed(msg)


class RaidSignupEmbed:
    def __init__(self, raid_title, worksheet_link, mention=None):
        self._embed = discord.Embed()
        self._embed.color = discord.Color.green()
        self._embed.title = raid_title
        self._embed.description = BASE_RAID_DESCRIPTION
        self._embed.add_field(name='DPS', value=0)
        self._embed.add_field(name='Healer', value=0)
        self._embed.add_field(name='Tank', value=0)
        if mention:
            self._embed.add_field(name='Host', value=mention)
        self._embed.url = worksheet_link

    @property
    def embed(self):
        return self._embed


def _is_raid_signup_title(embed):
    return (any([embed.title.startswith(k) for k in list(RAID_GROUP_DRAWER_MAP.keys())])
            or embed.title.startswith('Raid'))


async def _update_raid_embed(msg: discord.Message):
    embed = msg.embeds[0]
    dps = 0
    healer = 0
    tank = 0
    raid_worksheet = get_worksheet(embed.title)
    roles = col_values(raid_worksheet, 3)
    for role in roles:
        if role == 'dps':
            dps += 1
        elif role == 'healer':
            healer += 1
        elif role == 'tank':
            tank += 1
    embed.set_field_at(0, name='DPS', value=dps)
    embed.set_field_at(1, name='Healers', value=healer)
    embed.set_field_at(2, name='Tanks', value=tank)
    embed.description = BASE_RAID_DESCRIPTION
    await msg.edit(embed=embed)
