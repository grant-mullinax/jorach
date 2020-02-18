from datetime import datetime

from commands.info import Info
from commands.reporting import Reporting
from commands.management import *
from discord.ext.commands import Context
from providers.jorach_bot import *
from schema.roles import Role, get_all_roles
from schema.classes import get_all_classes
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
    )


def is_bot_identity_welcome_msg(msg, user):
    return (msg.author.id == bot.user.id
            and user.id != bot.user.id
            and len(msg.embeds) > 0
            and msg.embeds[0].title == IDENTITY_EMBED_TITLE
    )


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
                await user.send("Sorry, something went wrong!")
            await update_embed(msg)


async def raid_signup_helper(bot, channel, msg, user, guild, member, payload):
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
        # (Wangsly): This might be defunct now. You should no longer be able to see raid channels until
        # you have signed up at least one character. Once we've confirmed, let's remove this block.
        # TODO: Allow user to create an identity within messages from here
        await user.send("Sorry, but you'll need to register an identity before you can sign up for a raid! Please "
                        + "register your identity in the start-here channel. After that, un-react and then re-react to "
                        + "the raid signup post.")
        return

    chosen_row = None
    if len(user_profile_rows) == 1:
        # Only one row; auto-select the only row
        chosen_row = user_profile_rows[0]
    else:
        # Multiple rows; have to ask user which alt they want to use
        try:
            # Set up mapping between the identity and the row
            identity_to_row_map = {}
            user_identities = []
            for row in user_profile_rows:
                # 2 is the 0-index of the name column in the identity sheet
                k = row_values(identity_worksheet, row)[2].lower()
                identity_to_row_map[k] = row
                user_identities.append(k)
            user_choice = await prompt_choices("Which character would you like to sign up with?", user, user_identities)
            chosen_row = identity_to_row_map[user_choice]
        except Exception as e:
            print(e)
            await user.send("Oops! Something went wrong. Please try again!")
            return
        await user.send("Thank you! Your attendance has been recorded successfully.")

    identity_values = row_values(identity_worksheet, chosen_row)
    discord_id, name, wow_class, role = identity_values[1:5]
    names = col_values(raid_worksheet, 1)

    insert_row(raid_worksheet, [name, wow_class, role, str(datetime.now()), discord_id], len(names) + 1)

    # end garbage
    await update_embed(msg)

async def add_identity_helper(bot, channel, msg, user, guild, member, payload):
    # Remove the reaction immediately. We just want the button there to trigger the flow.
    await msg.remove_reaction(payload.emoji, user)
    author_id = str(member.id)

    try:
        name = await prompt_freeform("What is your character name?", user)
        wow_class = await prompt_choices("What is your class?", user, get_all_classes())
        wow_role = await prompt_choices("What is your role?", user, get_all_roles())

        identity_worksheet = get_identity_worksheet()

        rows_for_user_with_id = \
            get_rows_with_value_in_column(identity_worksheet, column_index=1, value_to_find=author_id)

        if rows_for_user_with_id:
            # The user has other profiles; make sure they don't duplicate an entry with the same character name
            rows_with_name_for_user_with_id = \
                get_rows_with_value_in_column(identity_worksheet, column_index=3, value_to_find=name.lower(),
                                              list_search_rows=rows_for_user_with_id)

            if rows_with_name_for_user_with_id:
                # Uh oh.. the user already registered a character with the same name! Tell them they STUPID.
                await user.send(("Unable to add profile: You already have a character named \"%s\"; " % name)
                                      + "did you mean to use `!editidentity`?")
                return
    except:
        user.send("Oops, something went wrong! Please try again.")
        return

    # Attempt to attach both a class role and the "Raider" role by default.
    # The "Ravenguard" role MUST be added by an admin manually because we have no way of
    # programmatically verifying it.
    raider_role = None
    class_role = None
    for role in guild.roles:
        if str(role).lower() == RAIDER_ROLE_NAME:
            raider_role = role
        elif str(role).lower() == wow_class.lower():
            class_role = role
        if class_role and raider_role:
            break
    if not raider_role:
        raider_role = await guild.create_role(name=RAIDER_ROLE_NAME)
    if not class_role:
        class_role = await guild.create_role(name=wow_class)
    await member.add_roles(raider_role, class_role)
    if not member.nick:
        try:
            await member.edit(nick=name)
        except:
            # This can fail if the member is too high up on the hierarchy (the bot can't change the nickname
            # of a server owner). Just let it slide for now.
            print("Could not change nickname for {}".format(member.name))

    # User does not have a character with the same name; class and role valid. Can register a new profile
    append_row(identity_worksheet, [author_id, str(user), name.lower(), wow_class.lower(), wow_role.lower()])
    await user.send("\"%s\" registered successfully." % name)




@bot.event
async def on_raw_reaction_add(payload):
    channel = bot.get_channel(payload.channel_id)
    msg = await channel.fetch_message(payload.message_id)
    user = bot.get_user(payload.user_id)
    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)
    if is_bot_raid_msg(msg, user):
        await raid_signup_helper(bot, channel, msg, user, guild, member, payload)
    elif is_bot_identity_welcome_msg(msg, user):
        await add_identity_helper(bot, channel, msg, user, guild, member, payload)

def check_message_from_user(user):
    def inner_check(message):
        return message.author == user

    return inner_check


secret = config["keys"]["DiscordSecret"]
bot.run(secret)
