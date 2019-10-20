from schema import Role, Spec


_spec_to_role = {
    Spec.arms: Role.dps,
    Spec.prot_warrior: Role.tank,
    Spec.fury: Role.dps,
    Spec.rogue: Role.dps,
    Spec.mage: Role.dps,
    Spec.warlock: Role.dps,
    Spec.hunter: Role.dps,
    Spec.holy: Role.healer,
    Spec.shadow: Role.dps,
    Spec.prot_paladin: Role.tank,
    Spec.holy: Role.healer,
    Spec.ret: Role.dps,
    Spec.resto: Role.healer,
    Spec.feral: Role.dps,
    Spec.bear: Role.tank,
}

def get_role_from_spec(spec: Spec) -> Role:
    role = _spec_to_role.get(spec, None)
    if role == None:
        raise Exception("Unable to find a role for spec: {}".format(spec))