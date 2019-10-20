from schema.roles import Role
from schema.specs import Spec


_spec_to_role = {
    # DPS
    Spec.arms: Role.dps,
    Spec.fury: Role.dps,
    Spec.rogue: Role.dps,
    Spec.mage: Role.dps,
    Spec.warlock: Role.dps,
    Spec.hunter: Role.dps,
    Spec.shadow: Role.dps,
    Spec.ret: Role.dps,
    Spec.feral: Role.dps,

    # Tanks
    Spec.prot_warrior: Role.tank,
    Spec.prot_paladin: Role.tank,
    Spec.bear: Role.tank,

    # Healers
    Spec.holy: Role.healer,
    Spec.resto: Role.healer,
    Spec.holy: Role.healer,
}

def get_role_from_spec(spec: Spec) -> Role:
    role = _spec_to_role.get(spec, None)
    if role == None:
        raise Exception("Unable to find a role for spec: {}".format(spec))
    return role