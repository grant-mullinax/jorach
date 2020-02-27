from datetime import datetime

from commands.info import Info
from commands.raid_management import Management
from identity.add import add_identity, is_bot_add_identity_msg
from identity.edit import edit_identity, is_bot_edit_identity_msg
from identity.remove import is_bot_remove_identity_msg, remove_identity
from providers.jorach_bot import get_jorach
from raid.loot_council import *
from raid.signup import *
from raid.start import *
from schema.classes import get_all_classes, get_class_roles
from schema.roles import Role, get_all_roles
from sheets.client import *

# Load configuration info
config = configparser.ConfigParser()
config.read_file(open('config.ini'))

# Get bot and register commands
bot = get_jorach()
bot.add_cog(Info())
bot.add_cog(Management())


# This sets how we handle raw reactions. Key is a condition function, value is a handler.
# Conditions and handlers all implement specific interfaces. Could abstract these, but lazy.
REACTION_MENU_MAP = {
    is_bot_raid_signup_msg: raid_signup,
    is_bot_add_identity_msg: add_identity,
    is_bot_edit_identity_msg: edit_identity,
    is_bot_remove_identity_msg: remove_identity,
    is_loot_council_control_msg: process_loot_council_control,
    is_raid_control_panel_msg: start_raid,
}


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.event
async def on_raw_reaction_remove(payload):
    channel, msg, user, guild, member = await parse_objs_from_payload(payload)
    try:
        if is_bot_raid_signup_msg(bot, msg, channel, user):
            await remove_raid_signup(bot, channel, msg, user, guild, member, payload)
    except Exception as e:
        await handle_error(user, msg, e)



@bot.event
async def on_raw_reaction_add(payload):
    channel, msg, user, guild, member = await parse_objs_from_payload(payload)
    try:
        for condition, handler in REACTION_MENU_MAP.items():
            if condition(bot, msg, channel, user):
                # The only time we don't want to immediately remove a reaction is for raid signup.
                if condition != is_bot_raid_signup_msg:
                    await msg.remove_reaction(payload.emoji, user)
                await handler(bot, channel, msg, user, guild, member, payload)
    except Exception as e:
        await handle_error(user, msg, e)


async def handle_error(user, msg, e):
        print('Error for user {} interacting with {}\nException: {}'.format(
            user.name, msg.embeds[0].title, str(e)))
        await user.send('Oops! Something went wrong {}'.format(str(e)))


async def parse_objs_from_payload(payload):
    channel = bot.get_channel(payload.channel_id)
    msg = await channel.fetch_message(payload.message_id)
    user = bot.get_user(payload.user_id)
    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)
    return (channel, msg, user, guild, member)


secret = config['keys']['DiscordSecret']
bot.run(secret)
