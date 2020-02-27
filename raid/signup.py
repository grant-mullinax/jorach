from datetime import datetime

import discord
from providers.jorach_bot import prompt_choices
from schema.constants import *
from sheets.client import *


def is_bot_raid_signup_msg(bot, msg, channel, user):
    """
    Returns true if the given message was posted by the bot,
    the user reacting is NOT the bot, AND the message embed title begins with
    a raid group name prefix (e.g. RG1, RG2, or Pub)
    """
    return (msg.author.id == bot.user.id
            and user.id != bot.user.id
            and len(msg.embeds) > 0
            and channel.category.name.lower() in [v.lower() for v in RAID_GROUP_DRAWER_MAP.values()]
            and (any([msg.embeds[0].title.startswith(k) for k in list(RAID_GROUP_DRAWER_MAP.keys())]) or msg.embeds[0].title.startswith('Raid'))
    )


async def raid_signup(bot, channel, msg, user, guild, member, payload):
    reactions = msg.reactions
    embed = msg.embeds[0]
    # Remove the reaction if the emoji isn't part of the raid signup process
    if str(payload.emoji) not in [SIGNUP_EMOJI]:
        await msg.remove_reaction(payload.emoji, user)
        return

    author_hash = str(user.id)
    raid_worksheet = get_worksheet(embed.title)
    user_profile_rows = get_rows_with_value_in_column(identity_worksheet, 1, author_hash)
    if not user_profile_rows:
        raise Exception('You need to register a character before you can sign ' \
            + 'up for raids! See the {} channel for info'.format(IDENTITY_MANAGEMENT_CHANNEL))

    chosen_row = None
    try:
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
    except Exception as e:
        print(e)
        await user.send('Oops! Something went wrong. {}'.format(str(e)))
        return

    identity_values = row_values(identity_worksheet, chosen_row)
    discord_id, name, wow_class, role = identity_values[1:5]
    names = col_values(raid_worksheet, 1)

    insert_row(raid_worksheet, [name, wow_class, role, str(datetime.now()), discord_id], len(names) + 1)

    await user.send('Thank you! Your attendance has been recorded successfully.')
    await update_embed(msg)


async def remove_raid_signup(bot, channel, msg, user, guild, member, payload):
    if str(payload.emoji) == SIGNUP_EMOJI:
        embed = msg.embeds[0]
        raid_worksheet = get_worksheet(embed.title)
        discord_ids = col_values(raid_worksheet, 5)
        try:
            delete_row(raid_worksheet, discord_ids.index(str(user)) + 1)
        except ValueError:
            # Treat deletion of an ID that doesn't exist as idempotent success
            pass
        await update_embed(msg)


async def update_embed(msg: discord.Message):
    """
    The close parameter here uses a ternary state (too lazy to make an enum):
    None means keep the current color
    Close = True means set color to red
    Close = False means set color to green
    """
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
