from datetime import datetime


SIGNUP_EMOJI = '☑'
INTERACT_EMOJI = '📩'
LOOT_COUNCIL_START_EMOJI = '✅'
LOOT_COUNCIL_STOP_EMOJI = '🛑'


ADD_IDENTITY_EMBED_TITLE = 'Add a New Identity'
ADD_IDENTITY_DESCRIPTION = 'In order to use this server, we require that you register a character identity.\n' \
    + 'Please click on the {} below to add a character identity.\n'.format(INTERACT_EMOJI) \
    + 'You can also use this flow to add alts.'


SELECT_MAIN_TITLE = 'Specify your main class'
SELECT_MAIN_DESCRIPTION = 'Because you guys keep whining about colors, you can specify your main class by reacting with the appropriate emoji'


SET_NICK_EMBED_TITLE = 'Change your nickname'
SET_NICK_DESCRIPTION = 'Customize your current nickname by clicking the {} button below.'.format(
    INTERACT_EMOJI)


EDIT_IDENTITY_EMBED_TITLE = 'Edit an Existing Identity'
EDIT_IDENTITY_DESCRIPTION = 'Please click on the {} below to edit an existing identity.\n'.format(INTERACT_EMOJI) \
    + 'You must have an existing identity for this to work.'


REMOVE_IDENTITY_EMBED_TITLE = 'Remove an Existing Identity'
REMOVE_IDENTITY_DESCRIPTION = 'Please click on the {} below to remove an existing identity.\n'.format(INTERACT_EMOJI) \
    + 'You must have an existing identity for this to work.'


LOOT_COUNCIL_EMBED_TITLE = 'Loot Council Control Panel'
LOOT_COUNCIL_CONTROL_DESCRIPTION = 'Press {} to start a loot council session.\n'.format(LOOT_COUNCIL_START_EMOJI) \
    + 'Press {} to end a loot council session.'.format(LOOT_COUNCIL_STOP_EMOJI)


RAID_CONTROL_EMBED_TITLE = 'Raid Control Panel'
RAID_CONTROL_EMBED_DESCRIPTION = 'Press {} to start a new raid.'.format(
    INTERACT_EMOJI)


BASE_RAID_DESCRIPTION = \
    'React with {} to register for this raid! Raid times are in server time (PST/PDT)\n\n'.format(SIGNUP_EMOJI) \
    + 'Note that is is your responsibility to confirm that you have been signed up properly.\n' \
    + 'If you run into an issue while signing up, please contact a moderator.'


START_HERE_CATEGORY = 'Public'
IDENTITY_MANAGEMENT_CHANNEL = 'identity-management'


RAID_GROUP_PUB = 'Pug'
RAID_GROUP_RG1 = 'RG1'
RAID_GROUP_RG2 = 'RG2'
RAID_GROUP_RG3 = 'RG3'
RAID_GROUP_20 = '20 RAID'
RAID_GROUP_AQ20 = 'AQ20'
RAVENGUARD_ROLE_MENTION = '<@&629419882387341332>'
PUG_RAIDER_ROLE_MENTION = '<@&679169414557597717>'
PUB_AND_RAVENGUARD_ROLE_MENTION = '{} {}'.format(
    PUG_RAIDER_ROLE_MENTION, RAVENGUARD_ROLE_MENTION)
RAID_GROUP_MENTION_ROLE_MAP = {
    RAID_GROUP_RG1: RAVENGUARD_ROLE_MENTION,
    RAID_GROUP_RG2: RAVENGUARD_ROLE_MENTION,
}


LC_ROLE = 'Loot Council'
RAID_CONTROLS_CHANNEL_SUFFIX = 'raid-controls'
RAID_VOICE_CHANNEL_CATEGORY = 'voice channels'
PUBLIC_RAID_DRAWER_CATEGORY = 'Public Raids'
RG1_RAID_DRAWER_CATEGORY = 'RG1 Raids'
RG2_RAID_DRAWER_CATEGORY = 'RG2 Raids'
RG3_RAID_DRAWER_CATEGORY = 'RG3 Raids'
TWENTY_PLAYER_RAID_DRAWER_CATEGORY = '20 Player Raids'
PUBLIC_RAID_CHANNEL = 'Public Raid'
RG1_RAID_CHANNEL = 'RG1 Raid'
RG2_RAID_CHANNEL = 'RG2 Raid'
RG3_RAID_CHANNEL = 'RG3 Raid'
RG1_LC_CHANNEL = 'RG1 Loot Council'
RG2_LC_CHANNEL = 'RG2 Loot Council'
RAIDER_ROLE_NAME = 'Raider'
RAVENGUARD_ROLE_NAME = 'Ravenguard'
RAID_GROUP_DRAWER_MAP = {
    RAID_GROUP_PUB: PUBLIC_RAID_DRAWER_CATEGORY,
    RAID_GROUP_RG1: RG1_RAID_DRAWER_CATEGORY,
    RAID_GROUP_RG2: RG2_RAID_DRAWER_CATEGORY,
    RAID_GROUP_RG3: RG3_RAID_DRAWER_CATEGORY,
    RAID_GROUP_20: TWENTY_PLAYER_RAID_DRAWER_CATEGORY,
}
RAID_GROUP_CHANNEL_MAP = {
    RAID_GROUP_RG1: RG1_RAID_CHANNEL,
    RAID_GROUP_RG2: RG2_RAID_CHANNEL,
}
RAID_GROUP_LC_CHANNEL_MAP = {
    RAID_GROUP_RG1: RG1_LC_CHANNEL,
    RAID_GROUP_RG2: RG2_LC_CHANNEL,
}
RAID_DRAWER_ALL_CHANNELS_MAP = {
    PUBLIC_RAID_DRAWER_CATEGORY: [PUBLIC_RAID_CHANNEL],
    RG1_RAID_DRAWER_CATEGORY: [RG1_RAID_CHANNEL, RG1_LC_CHANNEL],
    RG2_RAID_DRAWER_CATEGORY: [RG2_RAID_CHANNEL, RG2_LC_CHANNEL],
    RG3_RAID_DRAWER_CATEGORY: [RG3_RAID_CHANNEL],
}

RAID_DUNGEON_MC = 'MC'
RAID_DUNGEON_ONY = 'ONY'
RAID_DUNGEON_BWL = 'BWL'
RAID_DUNGEON_ZG = 'Zul\'Gurub'
RAID_DUNGEON_AQ20 = 'AQ20'
RAID_DUNGEON_AQ40 = 'AQ40'
RAID_DUNGEON_NAXX = 'NAXX'
RAID_DUNGEON_LIST = [
    RAID_DUNGEON_MC,
    RAID_DUNGEON_ONY,
    '{}-{}'.format(RAID_DUNGEON_MC, RAID_DUNGEON_ONY),
    RAID_DUNGEON_BWL,
    RAID_DUNGEON_ZG,  # PHASE 4
    RAID_DUNGEON_AQ20,
    RAID_DUNGEON_AQ40,  # PHASE 5
    RAID_DUNGEON_NAXX,  # PHASE 6
]

MONTHS = [datetime.strftime(datetime.strptime(
    str(x), '%m'), '%B') for x in range(1, 13)]
