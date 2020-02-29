from schema.constants import RAID_GROUP_DRAWER_MAP


def is_raid_category(channel):
    return channel.category.name.lower() in [v.lower() for v in RAID_GROUP_DRAWER_MAP.values()]
