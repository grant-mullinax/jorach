from datetime import datetime

from commands.info import Info
from commands.reporting import Reporting
from commands.management import *
from providers.jorach_bot import get_jorach
from schema.roles import Role
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


def is_bot_raid_msg(msg, user):
    return (msg.author.id == bot.user.id
            and user.id != bot.user.id
            and len(msg.embeds) > 0
            and msg.embeds[0].title.startswith("Raid - ")
    )


async def update_embed(msg: discord.Message, close=None):
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
        if role == "dps":
            dps += 1
        elif role == "healer":
            healer += 1
        elif role == "tank":
            tank += 1
    embed.set_field_at(0, name="DPS", value=dps)
    embed.set_field_at(1, name="Healers", value=healer)
    embed.set_field_at(2, name="Tanks", value=tank)
    embed.description = BASE_RAID_DESCRIPTION

    # if dps+healer+tank >= 1:
    #    embed.description += "\nThe raid is now full! Further responses will put you on the waitlist."

    # Specifically check for False. None is a different state.
    if close == False:
        embed.color = discord.Color.green()
    elif close == True:
        embed.color = discord.Color.red()
        embed.description += "\nSignups are closed!"
    await msg.edit(embed=embed)



@bot.event
async def on_raw_reaction_remove(payload):
    channel = bot.get_channel(payload.channel_id)
    msg = await channel.fetch_message(payload.message_id)
    user = await bot.fetch_user(payload.user_id)
    guild = await bot.fetch_guild(payload.guild_id)
    member = await guild.fetch_member(payload.user_id)
    if is_bot_raid_msg(msg, user):
        if str(payload.emoji) == SIGNUP_EMOJI:
            embed = msg.embeds[0]
            raid_worksheet = get_worksheet(embed.title)
            discord_ids = col_values(raid_worksheet, 5)
            try:
                delete_row(raid_worksheet, discord_ids.index(str(user)) + 1)
            except ValueError:
                # We might try to delete a raider ID that doesn't exist because they are trying to signup
                # while the form is closed. Rather than barf out an error, consume it somehow.
                await user.send("Sorry, signups for this raid are closed!")
            await update_embed(msg)
        if str(payload.emoji) == CLOSE_SIGNUP_EMOJI and channel.permissions_for(member).administrator:
            await update_embed(msg, close=False)


@bot.event
async def on_raw_reaction_add(payload):
    channel = bot.get_channel(payload.channel_id)
    msg = await channel.fetch_message(payload.message_id)
    user = await bot.fetch_user(payload.user_id)
    guild = await bot.fetch_guild(payload.guild_id)
    member = await guild.fetch_member(payload.user_id)
    if is_bot_raid_msg(msg, user):
        reactions = msg.reactions
        embed = msg.embeds[0]

        # Skip this entire process if the form is closed. Remove the reaction.
        # Also remove the reaction if the emoji isn't part of the raid signup process
        if embed.color == discord.Color.red() or str(payload.emoji) not in [SIGNUP_EMOJI, CLOSE_SIGNUP_EMOJI]:
            await msg.remove_reaction(payload.emoji, user)
            return

        # Fork the flow based on which of the signup emojis is sent. This is basically
        # a switch statement in the event pipeline here which is bad (could lead to a lot of branching)
        # but I don't understand the API enough yet to see a better way of handling this - Wangsly
        if str(payload.emoji) == CLOSE_SIGNUP_EMOJI and channel.permissions_for(member).administrator:
            await update_embed(msg, close=True)
            return

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
        author_hash = str(user.id)

        raid_worksheet = get_worksheet(embed.title)

        identity_values = None
        try:
            identity_values = row_values(identity_worksheet, discord_ids.index(author_hash) + 1)
        except ValueError:
            # TODO: Allow user to create an identity within messages from here
            await user.send("Sorry, but you'll need to register an identity before you can sign up for a raid! Please "
                            + "register your first (`!help identity`). After that, un-react and then re-react to "
                            + "the raid signup post.")
            return

        discord_id, name, wow_class, role = identity_values[1:5]
        names = col_values(raid_worksheet, 1)

        insert_row(raid_worksheet, [name, wow_class, role, str(datetime.now()), discord_id], len(names) + 1)

        # end garbage

        await update_embed(msg)


secret = config["keys"]["DiscordSecret"]
bot.run(secret)
