from discord.ext import commands


__bot_description = """My name is Jorach Ravenholdt and I'm here to help YOU raid.
Get started by using the !identity command.
!identity <name> <wow_class> <role>

look at my insides at
https://github.com/grant-mullinax/jorach
"""
__bot = commands.Bot(command_prefix="!", description=__bot_description, case_insensitive=True)


def get_jorach():
    """
    :return: The discord bot that is currently activate
    """
    return __bot

def get_chat_client():
