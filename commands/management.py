import discord
from discord.ext import commands

from providers.jorach_bot import get_jorach
from sheets.client import *


SIGNUP_EMOJI = "☑"
INTERACT_EMOJI = "📩"

IDENTITY_EMBED_TITLE = "Getting Started with Your Identity"
IDENTITY_REGISTRATION_DESCRIPTION = "In order to use this server, we require that you register a character identity.\n" \
    + "Please click on the reaction below to add a character identity (you can also use this flow to add alts)."

BASE_RAID_DESCRIPTION = \
    ("React with %s to register for this raid! Raid times are in server time (PST/PDT)" % SIGNUP_EMOJI) \
    + "\n\nNote that is is your responsibility to confirm that you have been signed up properly. If you run into an " \
    + "issue while signing up, please contact a moderator."
PRIVATE_RAID_DRAWER_CATEGORY = "raids"
PUBLIC_RAID_DRAWER_CATEGORY = "public raids"

START_HERE_CATEGORY = "welcome"
START_HERE_CHANNEL = "start-here"

RAID_TYPE_PUG = "pug"
RAID_TYPE_INHOUSE = "inhouse"

RAIDER_ROLE_NAME = "raider"

class Management(commands.Cog):

    """
    `Management` is a class that allows admin users to create raids for users
    """

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def bootstrap(self, ctx):
        # First, let's create the category if it's not already there.
        guild = ctx.message.guild
        categories = guild.categories
        category = None
        # Create the category if it's not already there.
        for c in categories:
            if c.name.lower() == START_HERE_CATEGORY:
                category = c
        if category == None:
            category = await guild.create_category(START_HERE_CATEGORY)

        # Do nothing if the channel is already made
        for c in category.channels:
            if c.name == START_HERE_CHANNEL:
                return

        channel = await category.create_text_channel(START_HERE_CHANNEL)

        embed = discord.Embed()
        embed.color = discord.Color.green()
        embed.title = IDENTITY_EMBED_TITLE
        embed.description = IDENTITY_REGISTRATION_DESCRIPTION

        msg = await channel.send(embed=embed)
        await msg.add_reaction(INTERACT_EMOJI)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def startraid(self, ctx):
        """
        Starts a new raid with a given name on a given date.

        Example: TODO

        DEVELOPER INFO:
        :param ctx: The context of invocation for the command that sheet was ran on.
        """
        # remove colons because it screws up some sheets calls, heh
        bot = get_jorach()
        finished = False
        user = ctx.message.author
        while not finished:
            await user.send("""
            What do you want to name the raid?
            """)
            user_msg = await bot.wait_for("message", check=check_message_from_user(user), timeout=60)
            raid_name = user_msg.content.lower().strip()
            if not raid_name:
                await user.send("Operation timed out. Please start the flow again")
                return

            await user.send("""
            What month do you want to hold the raid (e.g. 1 through 12)?
            """)
            user_msg = await bot.wait_for("message", check=check_message_from_user(user), timeout=60)
            raid_month = user_msg.content.lower().strip()
            if not raid_month:
                await user.send("Operation timed out. Please start the flow again")
                return

            await user.send("""
            What date do you want to hold the raid (e.g. 1 through 31)?
            """)
            user_msg = await bot.wait_for("message", check=check_message_from_user(user), timeout=60)
            raid_date = user_msg.content.lower().strip()
            if not raid_date:
                await user.send("Operation timed out. Please start the flow again")
                return

            await user.send("""
            What time do you want to hold the raid (e.g. 18:30)?
            """)
            user_msg = await bot.wait_for("message", check=check_message_from_user(user), timeout=60)
            raid_time = user_msg.content.lower().strip()
            if not raid_time:
                await user.send("Operation timed out. Please start the flow again")
                return
            await user.send("""
            Is this raid a pug or an inhouse?
            """)
            user_msg = await bot.wait_for("message", check=check_message_from_user(user), timeout=60)
            raid_type = user_msg.content.lower().strip()
            if not raid_time:
                await user.send("Operation timed out. Please start the flow again")
                return
            raid_category = None
            if raid_type == RAID_TYPE_PUG:
                raid_category = PUBLIC_RAID_DRAWER_CATEGORY
            elif raid_type == RAID_TYPE_INHOUSE:
                raid_category = PRIVATE_RAID_DRAWER_CATEGORY
            else:
                await user.send("Invalid raid type. Must be either 'pug' or 'inhouse'")
                return
            finished = True

        raid_title = "Raid - {} {}/{} @ {}".format(raid_name, raid_month, raid_date, raid_time).replace(":", "")
        safe_raid_name = raid_name.replace(" ", "-")
        channel_name = "{}-{}-{}".format(raid_title, raid_month, raid_date)
        # If the sheet is already made for whatever reason, just get it
        try:
            worksheet = duplicate_sheet(raid_title)
        except APIError:
            worksheet = get_worksheet(raid_title)

        embed = discord.Embed()
        embed.color = discord.Color.green()
        embed.title = raid_title
        embed.description = BASE_RAID_DESCRIPTION
        embed.add_field(name="DPS", value=0)
        embed.add_field(name="Healer", value=0)
        embed.add_field(name="Tank", value=0)
        embed.url = get_worksheet_link(worksheet)

        guild = ctx.message.guild
        categories = guild.categories
        category = None
        # Create the ca
        for c in categories:
            if c.name.lower() == raid_category:
                category = c
        if category == None:
            category = await guild.create_category(raid_category)

        safe_raid_name = raid_name.replace(" ", "-")
        channel_name = "{}-{}-{}".format(safe_raid_name, raid_month, raid_date)
        for c in category.channels:
            if c.name == channel_name:
                print("Already have a channel with this name, cancelling")
                return
        channel = await category.create_text_channel(channel_name)

        msg = await channel.send(embed=embed)
        await msg.add_reaction(SIGNUP_EMOJI)
        await user.send("Successfully created a raid in the {} category!".format(raid_category))
        return

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def deleteraid(self, ctx):
        channel = ctx.channel
        # Only delete channels in the `raids` category
        if channel.category.name.lower() in [PRIVATE_RAID_DRAWER_CATEGORY, PUBLIC_RAID_DRAWER_CATEGORY]:
            async for message in channel.history(limit=1, oldest_first=True):
                if len(message.embeds) > 0 and message.embeds[0].title.startswith("Raid -"):
                    sheet_title = message.embeds[0].title
                    try:
                        delete_worksheet(sheet_title)
                    except Exception:
                        print("Can't find the sheet {}".format(sheet_title))
                    await channel.delete()


def check_message_from_user(user):
    def inner_check(message):
        return message.author == user

    return inner_check