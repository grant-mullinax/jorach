from enum import Enum


class Role(Enum):
    dps = "dps"
    healer = "healer"
    tank = "tank"


def get_all_roles():
    return [c.value for c in Role]


def is_valid_role(role_name):
    return role_name.lower() in get_all_roles()
