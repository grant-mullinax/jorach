import discord
from sheets.client import *
from providers.jorach_bot import get_jorach
from datetime import datetime, timezone, timedelta
import asyncio

bot = get_jorach()
guild = bot.get_guild(552989099112529950)  # hardcoded to RG, add raid specific servers later.

LOCAL_TIMEZONE = timezone(timedelta(-8), "PST")


async def raid_reminder(rem_hours: int, rem_minutes: int, raid_title: str, channel_id: str):
    raid_worksheet = get_worksheet(raid_title)
    discord_ids = col_values(raid_worksheet, 6)
    raid_channel = guild.get_channel(channel_id)
    role = await guild.create_role(name=raid_title, mentionable=True)
    for snowflake in discord_ids:
        member = guild.get_member(snowflake)
        member.add_roles(role.id)
    raid_channel.send(
        content=str(role.mention + " reminder, this raid starts in " + rem_hours + "h" + rem_minutes + "m"))
    await role.delete()
    return


async def start_reminder_coroutine(channel_id: str, raid_title: str, raid_time: str):
    raid_datetime = datetime.fromisoformat(raid_time)
    seconds_until_raid = round((raid_datetime - datetime.now(LOCAL_TIMEZONE)).total_seconds())
    await asyncio.sleep(seconds_until_raid - 3600)
    raid_reminder(1, 0, raid_title, channel_id)
    return
