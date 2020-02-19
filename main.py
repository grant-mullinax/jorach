from datetime import datetime

from commands.info import Info
from commands.management import Management
from commands.reporting import Reporting
from identity.add import add_identity, is_bot_add_identity_msg
from identity.edit import edit_identity, is_bot_edit_identity_msg
from identity.remove import is_bot_remove_identity_msg, remove_identity
from providers.jorach_bot import get_jorach
from raid.signup import is_bot_raid_signup_msg, raid_signup, remove_raid_signup
from schema.classes import get_all_classes, get_class_roles
from schema.roles import Role, get_all_roles
from sheets.client import *

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


@bot.event
async def on_raw_reaction_remove(payload):
    channel, msg, user, guild, member = await parse_objs_from_payload(payload)
    if is_bot_raid_signup_msg(bot, msg, channel, user):
        remove_raid_signup(bot, channel, msg, user, guild, member, payload)


@bot.event
async def on_raw_reaction_add(payload):
    channel, msg, user, guild, member = await parse_objs_from_payload(payload)
    if is_bot_raid_signup_msg(bot, msg, channel, user):
        await raid_signup(bot, channel, msg, user, guild, member, payload)
    elif is_bot_add_identity_msg(bot, msg, channel, user):
        await add_identity(bot, channel, msg, user, guild, member, payload)
    elif is_bot_edit_identity_msg(bot, msg, channel, user):
        await edit_identity(bot, channel, msg, user, guild, member, payload)
    elif is_bot_remove_identity_msg(bot, msg, channel, user):
        await remove_identity(bot, channel, msg, user, guild, member, payload)


async def parse_objs_from_payload(payload):
    channel = bot.get_channel(payload.channel_id)
    msg = await channel.fetch_message(payload.message_id)
    user = bot.get_user(payload.user_id)
    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)
    return (channel, msg, user, guild, member)


secret = config["keys"]["DiscordSecret"]
bot.run(secret)
