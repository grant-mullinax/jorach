import discord
from discord.ext import commands

from providers.jorach_bot import *
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


START_HERE_CATEGORY = "General"
START_HERE_CHANNEL = "start-here"

RAID_TYPE_PUG = "Pug"
RAID_TYPE_RG1 = "RG1"
RAID_TYPE_RG2 = "RG2"

RG1_RAID_DRAWER_CATEGORY = "RG1 Raids"
RG2_RAID_DRAWER_CATEGORY = "RG2 Raids"
PUBLIC_RAID_DRAWER_CATEGORY = "Public Raids"

RAID_TYPE_DRAWER_MAP = {
    RAID_TYPE_PUG: PUBLIC_RAID_DRAWER_CATEGORY,
    RAID_TYPE_RG1: RG1_RAID_DRAWER_CATEGORY,
    RAID_TYPE_RG2: RG2_RAID_DRAWER_CATEGORY,
}


RAIDER_ROLE_NAME = "raider"

MONTHS = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]

class Management(commands.Cog):

    """
    `Management` is a class that allows admin users to create raids for users
    """
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def bootstrap(self, ctx):
        """
        Bootstraps the channels for welcoming new users if necessary.
        """
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

        DEVELOPER INFO:
        :param ctx: The context of invocation for the command that sheet was ran on.
        """
        # remove colons because it screws up some sheets calls, heh
        bot = get_jorach()
        finished = False
        user = ctx.message.author
        try:
            while not finished:
                raid_name = await prompt_freeform("What do you want to name the raid?\n" + \
                "(One word, alphanumeric only, e.g. `ony` or `bwl`)", user)
                raid_month = MONTHS.index(await prompt_choices("What month do you want to host the raid?", user, MONTHS)) + 1
                raid_date = await prompt_freeform("What date do you want to hold the raid (e.g. 1 through 31)", user)
                raid_time = await prompt_freeform("What time do you want to hold the raid? (Use military time, e.g. 18:30)", user)
                raid_type = await prompt_choices("What type of raid is this?", user, list(RAID_TYPE_DRAWER_MAP.keys()))
                raid_category = RAID_TYPE_DRAWER_MAP.get(raid_type, None)
                if not raid_category:
                    await user.send("Invalid raid type.")
                    return
                finished = True
        except:
            await user.send("Oops! Something went wrong. Please try again.")
            return

        raid_title = "{} - {} {}/{} @ {}".format(raid_type, raid_name, raid_month, raid_date, raid_time).replace(":", "")
        safe_raid_name = raid_name.replace(" ", "-")
        channel_name = "{}-{}-{}".format(raid_month, raid_date, raid_name)
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
        # Create the category
        for c in categories:
            if c.name.lower() == raid_category:
                category = c
        if category == None:
            category = await guild.create_category(raid_category)

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
        # Only delete channels in the raid categories
        print([v.lower() for v in RAID_TYPE_DRAWER_MAP.values()])
        if channel.category.name.lower() in [v.lower() for v in RAID_TYPE_DRAWER_MAP.values()]:
            async for message in channel.history(limit=1, oldest_first=True):
                if len(message.embeds) > 0:
                    sheet_title = message.embeds[0].title
                    try:
                        delete_worksheet(sheet_title)
                    except Exception:
                        await ctx.message.author.send("Failed to delete the associated sheet: {}".format(sheet_title))
                    await channel.delete()
