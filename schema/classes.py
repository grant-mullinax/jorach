from enum import Enum


class WowClass(Enum):
    druid = "druid"
    hunter = "hunter"
    mage = "mage"
    paladin = "paladin"
    rogue = "rogue"
    warlock = "warlock"
    warrior = "warrior"


def get_all_classes():
    return [c.value for c in WowClass]
