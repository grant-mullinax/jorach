from datetime import datetime

import discord
from discord.ext import commands
from pytz import timezone

from providers.jorach_bot import *
from schema.constants import *
from schema.util import *
from sheets.client import *


RAID_OTHER_PROMPT = 'What would you like to call the raid? ' \
    + 'Use alphanumeric characters and hyphens only [A-Za-z0-9] ' \
    + 'e.g. `onypickup2`, `aq40-group1`.'


class Management(commands.Cog):

    """
    `Management` is a class that allows admin users to create raids for users
    """
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def bootstrap(self, ctx):
        """

        DEVELOPER INFO:
        Bootstraps the channels for welcoming new users if necessary.
        """
        # First, let's create the category if it's not already there.
        guild = ctx.message.guild
        welcome_category = await create_category_if_not_exists(guild, START_HERE_CATEGORY)

        await self._setup_identity_controls(welcome_category)
        for raid_group, raid_category_name in RAID_GROUP_DRAWER_MAP.items():
            raid_category = await create_category_if_not_exists(guild, raid_category_name)
            await self._setup_raid_drawers(guild, raid_group)
            await self._setup_raid_voice_for_category(raid_category)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def deleteraid(self, ctx):
        """
        Deletes a raid when used in a raid signup channel (admin only)

        DEVELOPER INFO:
        :param ctx: Invocation context
        """
        channel = ctx.channel
        # Only delete channels in the raid categories
        if channel.category.name.lower() in [v.lower() for v in RAID_GROUP_DRAWER_MAP.values()]:
            async for message in channel.history(limit=1, oldest_first=True):
                if len(message.embeds) > 0:
                    sheet_title = message.embeds[0].title
                    try:
                        delete_worksheet(sheet_title)
                    except Exception:
                        await ctx.message.author.send('Failed to delete the associated sheet: {}'.format(sheet_title))
                    await channel.delete()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def notify(self, ctx):
        """
        Notifies all raiders signed up for a raid in a given raid channel.

        DEVELOPER INFO:
        :param ctx: Invocation context
        """
        channel = ctx.channel
        # This should only work in a raid channel
        if channel.category.name.lower() in [v.lower() for v in RAID_GROUP_DRAWER_MAP.values()]:
            async for message in channel.history(limit=1, oldest_first=True):
                if len(message.embeds) > 0:
                    sheet_title = message.embeds[0].title
                    raid_worksheet = get_worksheet(sheet_title)
                    ids = col_values(raid_worksheet, 5)
                    mention_str = ' '.join(['<@{}>'.format(
                        raider_id) for raider_id in ids])
                    notify_msg = await prompt_freeform('Enter the message you would like to blast to all signed up raiders.', ctx.message.author, timeout=180, preserve_fmt=True)
                    await channel.send('{}\n\n{}'.format(mention_str, notify_msg))

    async def _post_add_identity_embed(self, channel):
        embed = discord.Embed()
        embed.color = discord.Color.green()
        embed.title = ADD_IDENTITY_EMBED_TITLE
        embed.description = ADD_IDENTITY_DESCRIPTION

        msg = await channel.send(embed=embed)
        await msg.add_reaction(INTERACT_EMOJI)

    async def _post_edit_identity_embed(self, channel):
        embed = discord.Embed()
        embed.color = discord.Color.gold()
        embed.title = EDIT_IDENTITY_EMBED_TITLE
        embed.description = EDIT_IDENTITY_DESCRIPTION

        msg = await channel.send(embed=embed)
        await msg.add_reaction(INTERACT_EMOJI)

    async def _post_remove_identity_embed(self, channel):
        embed = discord.Embed()
        embed.color = discord.Color.red()
        embed.title = REMOVE_IDENTITY_EMBED_TITLE
        embed.description = REMOVE_IDENTITY_DESCRIPTION

        msg = await channel.send(embed=embed)
        await msg.add_reaction(INTERACT_EMOJI)

    async def _setup_raid_drawers(self, guild, raid_group):
        category_name = RAID_GROUP_DRAWER_MAP.get(raid_group, None)
        if category_name:
            category = await create_category_if_not_exists(guild, category_name)
            channel_name = '{}-{}'.format(raid_group,
                                          RAID_CONTROLS_CHANNEL_SUFFIX)
            existing_channel = find_by_name(
                category.text_channels, channel_name.lower())
            if not existing_channel:
                channel = await create_text_channel_if_not_exists(category, channel_name)
                await self._post_raid_control_embed(channel, raid_group)
                if raid_group.lower() != RAID_GROUP_PUB.lower():
                    await self._post_lc_control(channel, raid_group)

    async def _post_lc_control(self, channel, raid_group):
        embed = discord.Embed()
        embed.color = discord.Color.green()
        embed.title = '{} {}'.format(raid_group, LOOT_COUNCIL_EMBED_TITLE)
        embed.description = LOOT_COUNCIL_CONTROL_DESCRIPTION

        msg = await channel.send(embed=embed)
        await msg.add_reaction(LOOT_COUNCIL_START_EMOJI)
        await msg.add_reaction(LOOT_COUNCIL_STOP_EMOJI)

    async def _post_raid_control_embed(self, channel, raid_group):
        embed = discord.Embed()
        embed.color = discord.Color.green()
        embed.title = '{} {}'.format(raid_group, RAID_CONTROL_EMBED_TITLE)
        embed.description = RAID_CONTROL_EMBED_DESCRIPTION
        msg = await channel.send(embed=embed)
        await msg.add_reaction(INTERACT_EMOJI)

    async def _setup_identity_controls(self, category):
        # Do nothing if the channel is already made
        for c in category.channels:
            if c.name == IDENTITY_MANAGEMENT_CHANNEL:
                return

        channel = await category.create_text_channel(IDENTITY_MANAGEMENT_CHANNEL)

        await self._post_add_identity_embed(channel)
        await self._post_edit_identity_embed(channel)
        await self._post_remove_identity_embed(channel)

    async def _setup_raid_voice_for_category(self, category):
        for channel_name in RAID_DRAWER_ALL_CHANNELS_MAP.get(category.name, []):
            await create_voice_channel_if_not_exists(category, channel_name)
