from discord import User
from discord.ext import commands


__bot_description = """My name is Jorach Ravenholdt and I'm here to help YOU raid.
Get started by using the !addidentity command.
!addidentity <name> <wow_class> <role>

look at my insides at
https://github.com/grant-mullinax/jorach
"""
__bot = commands.Bot(command_prefix="!", description=__bot_description, case_insensitive=True)


def get_jorach():
    """
    :return: The discord bot that is currently activate
    """
    return __bot

async def prompt_freeform(msg: str, user: User) -> str:
    await user.send(msg)
    user_msg = await __bot.wait_for("message", check=check_message_from_user(user), timeout=60)
    content = user_msg.content.lower().strip()
    if not content:
        await user.send("Operation timed out.")
        raise Exception("Operation timed out.")
    return content

async def prompt_choices(msg_header: str, user: User, choices: list):
    msg = msg_header + "\nPlease select a choice by replying with the number of your selection"
    i = 1
    for choice in choices:
        part = "\n{}. {}".format(i, choice)
        msg += part
        i += 1
    selection = None
    while not selection:
        await user.send(msg)
        user_msg = await __bot.wait_for("message", check=check_message_from_user(user), timeout=60)
        content = user_msg.content.strip()
        if not content:
            await user.send("Operation timed out.")
            raise Exception("Operation timed out.")
        try:
            idx = int(content)
            if not (idx < len(choices) + 1):
                raise ValueError("Index out of range: {}. Must be between 1 and {}".format(idx, len(choices)))
        except:
            await user.send("Invalid selection. Please specify a valid number.")
        selection = choices[idx-1]
    return selection





def check_message_from_user(user):
    def inner_check(message):
        return message.author == user

    return inner_check