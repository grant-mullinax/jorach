from abc import ABC, abstractmethod


class EmbedMenu(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    async def check_message(self, channel, msg, user) -> bool:
        pass

    @abstractmethod
    async def handle_emoji(self, emoji, channel, msg, user, guild, member):
        pass

    async def execute(self, bot, emoji, channel, msg, user, guild, member):
        if self._is_human_reacting_to_bot_embed(bot, msg, user) \
                and await self.check_message(channel, msg, user):
            await self.handle_emoji(emoji, channel, msg, user, guild, member)

    def _is_human_reacting_to_bot_embed(self, bot, msg, user):
        return (msg.author.id == bot.user.id
                and user.id != bot.user.id
                and len(msg.embeds) > 0)
