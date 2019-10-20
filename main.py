import configparser

import discord

from Commands.CreateRaidCommand import CreateRaidCommand
from Commands.IdentityCommand import IdentityCommand
from Commands.OnyAttunementCommand import OnyAttunementCommand
from Commands.RaidsCommand import RaidsCommand
from Commands.RegisterCommand import *
from Commands.RolesCommand import RolesCommand
from Commands.SheetCommand import SheetCommand
from DataProviders.JorachBotProvider import get_jorach
from schema.emoji import get_emoji_map, get_spec_from_emoji
from schema.mapping import get_role_from_spec
from schema.roles import Role
from schema.specs import Spec


# Load configuration info
config = configparser.ConfigParser()
config.read_file(open('config.ini'))

# Get bot and register commands
bot = get_jorach()
bot.add_cog(IdentityCommand())
bot.add_cog(OnyAttunementCommand())
bot.add_cog(RaidsCommand(excluded_sheet_names=["identity", "template"]))
bot.add_cog(RegisterCommand())
bot.add_cog(RolesCommand())
bot.add_cog(SheetCommand())
bot.add_cog(CreateRaidCommand())


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
        await register_for_raid(channel, user, embed.title)
        await update_embed(msg)


secret = config["keys"]["DiscordSecret"]
bot.run(secret)
