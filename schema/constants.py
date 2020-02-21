from datetime import datetime


SIGNUP_EMOJI = "☑"
INTERACT_EMOJI = "📩"


ADD_IDENTITY_EMBED_TITLE = "Getting Started with Your Identity"
ADD_IDENTITY_DESCRIPTION = "In order to use this server, we require that you register a character identity.\n" \
    + "Please click on the reaction below to add a character identity (you can also use this flow to add alts)."


EDIT_IDENTITY_EMBED_TITLE = "Edit an Existing Identity"
EDIT_IDENTITY_DESCRIPTION = "Please click on the reaction below to edit an existing identity."


REMOVE_IDENTITY_EMBED_TITLE = "Remove an Existing Identity"
REMOVE_IDENTITY_DESCRIPTION = "Please click on the reaction below to remove an existing identity"


BASE_RAID_DESCRIPTION = \
    ("React with %s to register for this raid! Raid times are in server time (PST/PDT)" % SIGNUP_EMOJI) \
    + "\n\nNote that is is your responsibility to confirm that you have been signed up properly. If you run into an " \
    + "issue while signing up, please contact a moderator."


START_HERE_CATEGORY = "General"
START_HERE_CHANNEL = "start-here"


RAID_TYPE_PUG = "Pug"
RAID_TYPE_RG1 = "RG1"
RAID_TYPE_RG2 = "RG2"
RAVENGUARD_ROLE_MENTION = "<@&629419882387341332>"
PUG_RAIDER_ROLE_MENTION = "<@&679169414557597717>"

RAID_TYPE_MENTION_ROLE_MAP = {
    RAID_TYPE_PUG: "{} {}".format(PUG_RAIDER_ROLE_MENTION, RAVENGUARD_ROLE_MENTION),
    RAID_TYPE_RG1: RAVENGUARD_ROLE_MENTION,
    RAID_TYPE_RG2: RAVENGUARD_ROLE_MENTION,
}


LC_ROLE = "LootCouncil"
RG1_RAID_DRAWER_CATEGORY = "RG1 Raids"
RG2_RAID_DRAWER_CATEGORY = "RG2 Raids"
RG1_RAID_CHANNEL = "RG1 Raid"
RG2_RAID_CHANNEL = "RG2 Raid"
RG1_LC_CHANNEL = "RG1 Loot Council"
RG2_LC_CHANNEL = "RG2 Loot Council"
PUBLIC_RAID_DRAWER_CATEGORY = "Public Raids"
RAIDER_ROLE_NAME = "raider"
RAID_TYPE_DRAWER_MAP = {
    RAID_TYPE_PUG: PUBLIC_RAID_DRAWER_CATEGORY,
    RAID_TYPE_RG1: RG1_RAID_DRAWER_CATEGORY,
    RAID_TYPE_RG2: RG2_RAID_DRAWER_CATEGORY,
}
RAID_TYPE_RAID_CHANNEL_MAP = {
    RAID_TYPE_RG1: RG1_RAID_CHANNEL,
    RAID_TYPE_RG2: RG2_RAID_CHANNEL,
}
RAID_TYPE_LC_CHANNEL_MAP = {
    RAID_TYPE_RG1: RG1_LC_CHANNEL,
    RAID_TYPE_RG2: RG2_LC_CHANNEL,
}

MONTHS = [datetime.strftime(datetime.strptime(str(x), "%m"), "%B") for x in range(1,13)]