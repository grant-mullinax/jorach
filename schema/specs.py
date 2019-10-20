from enum import Enum


class Spec(Enum):
    # Warrior stuff
    arms = "arms"
    prot_warrior = "prot warrior"
    fury = "fury"

    # Classes that collapse into a single role type (e.g. all specs in Rogue are DPS)
    rogue = "rogue"
    mage = "mage"
    warlock = "warlock"
    hunter = "hunter"

    # Priest stuff
    holy = "holy priest"
    shadow = "shadow priest"

    # Paladin stuff
    prot_paladin = "prot paladin"
    holy_paladin = "holy paladin"
    ret = "retribution"

    # Druid stuff
    resto = "restoration"
    feral = "feral"
    bear = "bear"
