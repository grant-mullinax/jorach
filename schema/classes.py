from enum import Enum
from schema.roles import Role


CLASS_ROLE_MAP = {
    "druid": [Role.dps.value, Role.healer.value, Role.tank.value],
    "hunter": [Role.dps.value],
    "mage": [Role.dps.value],
    "paladin": [Role.dps.value, Role.healer.value, Role.tank.value],
    "priest": [Role.dps.value, Role.healer.value],
    "rogue": [Role.dps.value],
    "shaman": [Role.dps.value, Role.healer.value],
    "warlock": [Role.dps.value],
    "warrior": [Role.dps.value, Role.tank.value],
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