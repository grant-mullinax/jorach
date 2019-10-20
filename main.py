import configparser

import discord

from commands.info import Info
from commands.reporting import Reporting
from commands.management import Management
from DataProviders.JorachBotProvider import get_jorach
from schema.emoji import get_emoji_map, get_spec_from_emoji
from schema.mapping import get_role_from_spec
from schema.roles import Role
from schema.specs import Spec

from sheets.client import *
from datetime import datetime

# Load configuration info
config = configparser.ConfigParser()
config.read_file(open('config.ini'))

# Get bot and register commands
bot = get_jorach()
bot.add_cog(Info())
bot.add_cog(Reporting())
bot.add_cog(Management())


@bot.event
async def on_ready():
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print("------")


def is_bot_raid_msg(msg, user):
    return (msg.author.id == bot.user.id
            and user.id != bot.user.id
            and len(msg.embeds) > 0
            and msg.embeds[0].title.startswith("Raid - ")
    )


async def update_embed(msg: discord.Message):
    reactions = msg.reactions
    embed = msg.embeds[0]
    dps = 0
    healer = 0
    tank = 0
    for r in reactions:
        # Never count the bot's reaction
        count = r.count - 1
        spec = get_spec_from_emoji(str(r.emoji))
        role = get_role_from_spec(spec)
        if role == Role.dps:
            dps += count
        elif role == Role.healer:
            healer += count
        elif role == Role.tank:
            tank += count
    embed.set_field_at(0, name="DPS", value=dps)
    embed.set_field_at(1, name="Healers", value=healer)
    embed.set_field_at(2, name="Tanks", value=tank)
    await msg.edit(embed=embed)



@bot.event
async def on_raw_reaction_remove(payload):
    channel = bot.get_channel(payload.channel_id)
    msg = await channel.fetch_message(payload.message_id)
    user = await bot.fetch_user(payload.user_id)
    if is_bot_raid_msg(msg, user):
        await update_embed(msg)


@bot.event
async def on_raw_reaction_add(payload):
    channel = bot.get_channel(payload.channel_id)
    msg = await channel.fetch_message(payload.message_id)
    user = await bot.fetch_user(payload.user_id)
    if is_bot_raid_msg(msg, user):
        reactions = msg.reactions
        embed = msg.embeds[0]

        # Skip this entire process if the form is closed. Remove the reaction.
        # Also remove the reaction if the emoji isn't part of the raid signup process
        if embed.color == discord.Color.red() or str(payload.emoji) not in get_emoji_map().keys():
            await msg.remove_reaction(payload.emoji, user)
            return

        for r in reactions:
            users = r.users()
            users = await users.flatten()
            for u in users:
                if user.id == u.id and r.emoji != payload.emoji:
                    await msg.remove_reaction(r.emoji, user)

        # await register_for_raid(channel, user, embed.title)

        # i started reworking the whole command system thing and got here last and realized why you split the
        # functionality out of the register class. whoops. ultimately though I think we'll need a different way
        # of talking to the user because spamming the raid registration channel with error messages or confirmations
        # will make the raid message hard to find, so I got rid of all the error reporting and just slapped it here.
        # eventually we'll want to split this and what happens in register off into its own thing to prevent
        # code duplication. the plan is to just have it throw exceptions on the errors (like no identity)
        # and just let whatever is calling it deal with relaying that to the user

        # start garbage

        discord_ids = col_values(identity_worksheet, 1)
        author_hash = str(hash(user))

        raid_worksheet = get_worksheet(embed.title)
        identity_values = row_values(identity_worksheet, discord_ids.index(author_hash) + 1)

        name, wow_class, role = identity_values[2:5]
        names = col_values(raid_worksheet, 1)

        insert_row(raid_worksheet, [name, wow_class, role, str(datetime.now())], len(names) + 1)

        # end garbage

        await update_embed(msg)


secret = config["keys"]["DiscordSecret"]
bot.run(secret)
