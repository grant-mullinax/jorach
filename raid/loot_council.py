from menus.embed import EmbedMenu
from raid.util import is_raid_category
from schema.constants import *
from schema.util import find_by_name


class LootCouncilMenu(EmbedMenu):
    async def check_message(self, channel, msg, user) -> bool:
        return is_raid_category(channel) and _is_loot_council_embed_title(msg.embeds[0])

    async def handle_emoji(self, emoji, channel, msg, user, guild, member):
        await msg.remove_reaction(emoji, user)
        k = _get_raid_type_from_embed(msg)
        str_emoji = str(emoji)
        if str_emoji == LOOT_COUNCIL_START_EMOJI:
            return await _loot_council_start(user, guild, k)
        elif str_emoji == LOOT_COUNCIL_STOP_EMOJI:
            return await _loot_council_end(user, guild, k)

def _is_loot_council_embed_title(embed):
    return any([embed.title == '{} {}'.format(k, LOOT_COUNCIL_EMBED_TITLE)
                for k in list(RAID_GROUP_DRAWER_MAP.keys())])

async def process_loot_council_control(bot, channel, msg, user, guild, member, payload):
    k = _get_raid_type_from_embed(msg)
    str_emoji = str(payload.emoji)
    if str_emoji == LOOT_COUNCIL_START_EMOJI:
        return await _loot_council_start(user, guild, k)
    elif str_emoji == LOOT_COUNCIL_STOP_EMOJI:
        return await _loot_council_end(user, guild, k)


async def _loot_council_start(user, guild, raid_type):
    await _channel_move_helper(
        user,
        guild,
        RAID_GROUP_DRAWER_MAP.get(raid_type, None),
        RAID_GROUP_CHANNEL_MAP.get(raid_type, None),
        RAID_GROUP_LC_CHANNEL_MAP.get(raid_type, None),
    )


async def _loot_council_end(user, guild, raid_type):
    await _channel_move_helper(
        user,
        guild,
        RAID_GROUP_DRAWER_MAP.get(raid_type, None),
        RAID_GROUP_LC_CHANNEL_MAP.get(raid_type, None),
        RAID_GROUP_CHANNEL_MAP.get(raid_type, None),
    )


def _get_raid_type_from_embed(msg):
    tokens = msg.embeds[0].title.split(' ')
    return tokens[0].upper()


async def _channel_move_helper(user, guild, raid_drawer_name, src_channel_name, dest_channel_name):
    if not src_channel_name or not dest_channel_name or not raid_drawer_name:
        await user.send('Invalid raid type, please specify any of {}'.format(
            str(list(RAID_GROUP_CHANNEL_MAP.keys())).replace('\'', '')))
        return
    category = find_by_name(guild.categories, raid_drawer_name)
    if not category:
        await user.send('Could not find the loot council voice channel')
        return
    channels = category.voice_channels
    src_channel = find_by_name(category.voice_channels, src_channel_name)
    dest_channel = find_by_name(category.voice_channels, dest_channel_name)
    if not src_channel or not dest_channel:
        await user.send('Couldn not find the loot council voice channel')
        return
    role = find_by_name(guild.roles, LC_ROLE)
    if not role:
        await user.send('Could not find loot council role: {}'.format(LC_ROLE))
        return
    for member in src_channel.members:
        if role in member.roles:
            await member.move_to(dest_channel)