from datetime import datetime

from commands.info import Info
from commands.raid_management import Management
from identity.add import AddIdentityMenu
from identity.edit import EditIdentityMenu
from identity.remove import RemoveIdentityMenu
from providers.jorach_bot import get_jorach
from raid.loot_council import LootCouncilMenu
from raid.signup import RaidDeregisterMenu, RaidSignupMenu
from raid.start import StartRaidMenu
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


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


# Define the sets of handlers for each reaction type (add and remove)
ADD_REACTION_MENUS = [
    # Raid Management
    RaidSignupMenu(),
    StartRaidMenu(),
    # Identity
    AddIdentityMenu(),
    EditIdentityMenu(),
    RemoveIdentityMenu(),
    # Loot Council
    LootCouncilMenu(),
]
REMOVE_REACTION_MENUS = [
    RaidDeregisterMenu(),
]


@bot.event
async def on_raw_reaction_remove(payload):
    args = await parse_objs_from_payload(payload)
    try:
        for menu in REMOVE_REACTION_MENUS:
            await menu.execute(bot, *args)
    except Exception as e:
        await handle_error(*args, e)



@bot.event
async def on_raw_reaction_add(payload):
    args = await parse_objs_from_payload(payload)
    try:
        for menu in ADD_REACTION_MENUS:
            await menu.execute(bot, *args)
    except Exception as e:
        await handle_error(*args, e)


async def handle_error(emoji, channel, msg, user, guild, member, e):
        print('Error for user {} interacting with {}\nException: {}'.format(
            user.name, msg.embeds[0].title, str(e)))
        await user.send('Oops! Something went wrong {}'.format(str(e)))


async def parse_objs_from_payload(payload):
    emoji = payload.emoji
    channel = bot.get_channel(payload.channel_id)
    msg = await channel.fetch_message(payload.message_id)
    user = bot.get_user(payload.user_id)
    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)
    return (emoji, channel, msg, user, guild, member)


secret = config['keys']['DiscordSecret']
bot.run(secret)
