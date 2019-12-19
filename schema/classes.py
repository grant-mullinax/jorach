from enum import Enum


class WowClass(Enum):
    druid = "druid"
    hunter = "hunter"
    mage = "mage"
    paladin = "paladin"
    priest = "priest"
    rogue = "rogue"
    shaman = "shaman"
    warlock = "warlock"
    warrior = "warrior"


def get_all_classes():
    return [c.value for c in WowClass]


def is_valid_class(class_name):
    return class_name.lower() in get_all_classes()
