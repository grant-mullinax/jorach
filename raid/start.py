from datetime import datetime

import discord
from pytz import timezone

from providers.jorach_bot import prompt_choices, prompt_choices_other, prompt_freeform
from schema.constants import *
from schema.util import create_category_if_not_exists, find_by_name
from sheets.client import *


_RAID_OTHER_PROMPT = 'What would you like to call the raid? ' \
    + 'Use alphanumeric characters and hyphens only [A-Za-z0-9] ' \
    +'e.g. `onypickup2`, `aq40-group1`.'


def is_raid_control_panel_msg(bot, msg, channel, user):
    """
    Returns true if the given message was posted by the bot,
    the user reacting is NOT the bot, AND the message embed tile is the raid control title
    """
    return (msg.author.id == bot.user.id
            and user.id != bot.user.id
            and len(msg.embeds) > 0
            and channel.category.name.lower() in [v.lower() for v in RAID_GROUP_DRAWER_MAP.values()]
            and (any([msg.embeds[0].title == '{} {}'.format(k, RAID_CONTROL_EMBED_TITLE)
                for k in list(RAID_GROUP_DRAWER_MAP.keys())]))
    )


async def start_raid(bot, channel, msg, user, guild, member, payload):
    """
    Starts a new raid (admin only)

    DEVELOPER INFO:
    :param ctx: The context of invocation for the command that sheet was ran on.
    """
    raid_name = await prompt_choices_other('What type of raid would you like to start?',
        _RAID_OTHER_PROMPT, member, RAID_DUNGEON_LIST)
    raid_month = MONTHS.index(await prompt_choices('What month do you want to host the raid?', member, MONTHS)) + 1
    raid_date = int(await prompt_freeform('What date do you want to hold the raid (e.g. 1 through 31)', member))
    today = timezone('US/Pacific').localize(datetime.now())
    year = today.year
    # Assume we are in the year ahead if given a date that is 'less than' today
    if raid_month < today.month or (raid_month == today.month and today.day > raid_date):
        year += 1
    t = datetime(year, raid_month, raid_date)
    raid_day = datetime.strftime(t, '%a').lower()
    raid_time = await prompt_freeform('What time do you want to hold the raid? (Use military time, e.g. 18:30)', user)
    raid_category = channel.category.name
    raid_drawer_group_map = {v: k for k, v in RAID_GROUP_DRAWER_MAP.items()}
    raid_group = raid_drawer_group_map.get(raid_category, None)
    role_mention = RAID_GROUP_MENTION_ROLE_MAP.get(raid_group, None)
    if not raid_category or not role_mention:
        raise Exception('Invalid raid group.')


    # remove colons because it screws up some sheets calls, heh
    raid_title = '{} - {} {} {}/{} @ {}'.format(raid_group, raid_name.title(),
        raid_day.title(), raid_month, raid_date, raid_time).replace(':', '')
    channel_name = '{}-{}-{}-{}'.format(raid_month, raid_date, raid_day, raid_name)
    # If the sheet is already made for whatever reason, just get it
    try:
        worksheet = duplicate_sheet(raid_title)
    except APIError:
        worksheet = get_worksheet(raid_title)

    embed = discord.Embed()
    embed.color = discord.Color.green()
    embed.title = raid_title
    embed.description = BASE_RAID_DESCRIPTION
    embed.add_field(name='DPS', value=0)
    embed.add_field(name='Healer', value=0)
    embed.add_field(name='Tank', value=0)
    embed.url = get_worksheet_link(worksheet)

    category = await create_category_if_not_exists(msg.guild, raid_category)
    duplicate_channel = find_by_name(category.channels, channel_name)
    if duplicate_channel:
        await user.send('Already have a channel for this raid, cancelling.')
        return
    channel = await category.create_text_channel(channel_name)

    msg = await channel.send(embed=embed)
    await msg.add_reaction(SIGNUP_EMOJI)
    await channel.send('New raid signups are open! {}'.format(role_mention))
    await user.send('Successfully created a raid in the {} category!'.format(raid_category))
