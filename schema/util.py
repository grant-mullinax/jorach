def find_by_name(l, id: str):
    for x in l:
        if x.name.lower() == id.lower():
            return x
    return None


async def create_category_if_not_exists(guild, category_name):
    category = find_by_name(guild.categories, category_name.lower())
    if category == None:
        category = await guild.create_category(category_name)
    return category


async def create_voice_channel_if_not_exists(category, channel_name):
    channel = find_by_name(category.voice_channels, channel_name.lower())
    if channel == None:
        channel = await category.create_voice_channel(channel_name)
    return channel


async def create_text_channel_if_not_exists(category, channel_name):
    channel = find_by_name(category.text_channels, channel_name.lower())
    if channel == None:
        channel = await category.create_text_channel(channel_name)
    return channel