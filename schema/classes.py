from enum import Enum
from schema.roles import Role


CLASS_ROLE_MAP = {
    'Druid': [Role.dps.value, Role.healer.value, Role.tank.value],
    'Hunter': [Role.dps.value],
    'Mage': [Role.dps.value],
    'Paladin': [Role.dps.value, Role.healer.value, Role.tank.value],
    'Priest': [Role.dps.value, Role.healer.value],
    'Rogue': [Role.dps.value],
    # 'Shaman': [Role.dps.value, Role.healer.value],
    'Warlock': [Role.dps.value],
    'Warrior': [Role.dps.value, Role.tank.value],
}


CLASS_COLORS_MAP = {
    'Druid': 0xFF7D0A,
    'Hunter': 0xABD473,
    'Mage': 0x69CCF0,
    'Paladin': 0xF58CBA,
    # Not the real color but people actually use the white background on Discord soooo
    'Priest': 0xCCCCCC,
    'Rogue': 0xFFF569,
    # 'Shaman': 0x0070DE,
    'Warlock': 0x9482C9,
    'Warrior': 0xC79C6E,
}


CLASS_EMOTE_MAP = {
    615267826034409482: 'Druid',
    615267826126553096: 'Hunter',
    615267826382536726: 'Mage',
    615267825967169551: 'Paladin',
    615267825937940481: 'Priest',
    615267826382536865: 'Rogue',
    # 615267826160369674: 'Shaman',
    615267826042929153: 'Warlock',
    615267826223022100: 'Warrior',
}


class WowClass(Enum):
    druid = 'Druid'
    hunter = 'Hunter'
    mage = 'Mage'
    paladin = 'Paladin'
    priest = 'Priest'
    rogue = 'Rogue'
    # shaman = 'Shaman'
    warlock = 'Warlock'
    warrior = 'Warrior'


def get_all_classes():
    return [c.value for c in WowClass]


def is_valid_class(class_name):
    return class_name.lower() in get_all_classes()


def get_class_roles(cls: str):
    return CLASS_ROLE_MAP.get(cls, [])
