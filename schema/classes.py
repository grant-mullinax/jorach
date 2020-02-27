from enum import Enum
from schema.roles import Role


CLASS_ROLE_MAP = {
    'Druid': [Role.dps.value, Role.healer.value, Role.tank.value],
    'Hunter': [Role.dps.value],
    'Mage': [Role.dps.value],
    'Paladin': [Role.dps.value, Role.healer.value, Role.tank.value],
    'Priest': [Role.dps.value, Role.healer.value],
    'Rogue': [Role.dps.value],
    'Shaman': [Role.dps.value, Role.healer.value],
    'Warlock': [Role.dps.value],
    'Warrior': [Role.dps.value, Role.tank.value],
}


class WowClass(Enum):
    druid = 'Druid'
    hunter = 'Hunter'
    mage = 'Mage'
    paladin = 'Paladin'
    priest = 'Priest'
    rogue = 'Rogue'
    shaman = 'Shaman'
    warlock = 'Warlock'
    warrior = 'Warrior'


def get_all_classes():
    return [c.value for c in WowClass]


def is_valid_class(class_name):
    return class_name.lower() in get_all_classes()


def get_class_roles(cls: str):
    return CLASS_ROLE_MAP.get(cls, [])