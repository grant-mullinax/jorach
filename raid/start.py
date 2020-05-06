from datetime import datetime

import discord
from pytz import timezone

from menus.embed import EmbedMenu
from providers.jorach_bot import prompt_choices, prompt_choices_other, prompt_freeform
from raid.signup import RaidSignupEmbed
from raid.util import is_raid_category
from schema.constants import *
from schema.util import create_category_if_not_exists, find_by_name
from sheets.client import *


_RAID_OTHER_PROMPT = 'What would you like to call the raid? ' \
    + 'Use alphanumeric characters and hyphens only [A-Za-z0-9] ' \
    + 'e.g. `onypickup2`, `aq40-group1`.'


class StartRaidMenu(EmbedMenu):
    async def check_message(self, channel, msg, user) -> bool:
        """
        Returns true if the message embed tile is the raid control title
        """
        return is_raid_category(channel) and _is_raid_control_panel_title(msg)

    async def handle_emoji(self, emoji, channel, msg, user, guild, member):
        await msg.remove_reaction(emoji, user)
        raid_category = channel.category.name
        raid_group = _get_raid_group(raid_category)

        if raid_group == RAID_GROUP_ZG:
            raid_name = await prompt_freeform('What is the name of your raid group?\n(e.g. `Megasharks`, `Besaid Barcas`, `Wangsly and the Jets`).\nPlease keep it short and use alphanum only so nothing breaks. Kthx', user)
        else:
            raid_name = await prompt_choices_other('What type of raid would you like to start?',
                                               _RAID_OTHER_PROMPT, member, RAID_DUNGEON_LIST)
        raid_month, raid_date, raid_day = await _get_raid_date(member)
        raid_time = await prompt_freeform('What time do you want to hold the raid? (Use military time, e.g. 18:30)', user)

        role_mention = RAID_GROUP_MENTION_ROLE_MAP.get(raid_group, None)
        if not raid_category:
            raise Exception('Invalid raid group.')

        # remove colons because it screws up some sheets calls, heh
        raid_title = '{} - {} {} {}/{} @ {}'.format(raid_group, raid_name.title(),
                                                    raid_day.title(), raid_month, raid_date, raid_time).replace(':', '')
        channel_name = '{}-{}-{}-{}'.format(raid_month,
                                            raid_date, raid_day, raid_name)
        # If the sheet is already made for whatever reason, just get it
        try:
            worksheet = duplicate_sheet(raid_title)
        except APIError:
            worksheet = get_worksheet(raid_title)

        category = await create_category_if_not_exists(msg.guild, raid_category)
        duplicate_channel = find_by_name(category.channels, channel_name)
        if duplicate_channel:
            await user.send('Already have a channel for this raid, cancelling.')
            return
        channel = await category.create_text_channel(channel_name)
        mention = None
        if raid_group == RAID_GROUP_ZG:
            mention = user.mention
        msg = await channel.send(embed=RaidSignupEmbed(raid_title, get_worksheet_link(worksheet), mention=mention).embed)
        await msg.add_reaction(SIGNUP_EMOJI)
        if role_mention:
            await channel.send('New raid signups are open! {}'.format(role_mention))
        await user.send('Successfully created a raid in the {} category!'.format(raid_category))


def _is_raid_control_panel_title(msg):
    return any([msg.embeds[0].title == '{} {}'.format(k, RAID_CONTROL_EMBED_TITLE)
                for k in list(RAID_GROUP_DRAWER_MAP.keys())])


async def _get_raid_date(member):
    raid_month = MONTHS.index(await prompt_choices('What month do you want to host the raid?', member, MONTHS)) + 1
    raid_date = int(await prompt_freeform('What date do you want to hold the raid (e.g. 1 through 31)', member))
    today = timezone('US/Pacific').localize(datetime.now())
    year = today.year
    # Assume we are in the year ahead if given a date that is 'less than' today
    if raid_month < today.month or (raid_month == today.month and today.day > raid_date):
        year += 1
    t = datetime(year, raid_month, raid_date)
    raid_day = datetime.strftime(t, '%a').lower()
    return raid_month, raid_date, raid_day


def _get_raid_group(raid_category):
    raid_drawer_group_map = {v: k for k, v in RAID_GROUP_DRAWER_MAP.items()}
    raid_group = raid_drawer_group_map.get(raid_category, None)
    return raid_group
