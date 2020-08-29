from menus.embed import EmbedMenu
from providers.jorach_bot import prompt_freeform
from schema.constants import *
from sheets.client import *


class SetNicknameMenu(EmbedMenu):
    async def check_message(self, channel, msg, user) -> bool:
        """
        Returns true if the message embed title is the add identity title
        """
        return channel.category.name == START_HERE_CATEGORY \
            and msg.embeds[0].title == SET_NICK_EMBED_TITLE

    async def handle_emoji(self, emoji, channel, msg, user, guild, member):
        await msg.remove_reaction(emoji, user)
        if str(emoji) == INTERACT_EMOJI:
            nickname = await prompt_freeform('Please enter your nickname. Note that this will not work if you are an admin.'
                                             + 'If you are an admin, just change your nickname manually.',
                                             user,
                                             preserve_fmt=True
                                             )
            await member.edit(nick=nickname)
        return
