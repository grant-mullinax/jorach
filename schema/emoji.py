from schema.specs import Spec


__emoji_to_spec = {
    '<:Warrior:635287268369891329>': Spec.fury,
    '<:ProtWarrior:635287268529274880>': Spec.prot_warrior,
}

def get_emoji_map():
    return __emoji_to_spec

def get_spec_from_emoji(emoji: str):
    return __emoji_to_spec.get(emoji, None)