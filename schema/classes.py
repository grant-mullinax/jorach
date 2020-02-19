from enum import Enum
from schema.roles import Role


CLASS_ROLE_MAP = {
    "druid": [Role.dps, Role.healer, Role.tank],
    "hunter": [Role.dps],
    "mage": [Role.dps],
    "paladin": [Role.dps, Role.healer, Role.tank],
    "priest": [Role.dps, Role.healer],
    "rogue": [Role.dps],
    "shaman": [Role.dps, Role.healer],
    "warlock": [Role.dps],
    "warrior": [Role.dps, Role.tank],
}


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


def get_class_roles(cls: str):
    return CLASS_ROLE_MAP.get(cls, [])