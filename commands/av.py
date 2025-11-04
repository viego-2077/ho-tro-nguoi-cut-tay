import discord
import os

name = "av"

async def run(message, args):
    user = message.author

    if message.mentions:
        user = message.mentions[0]

    avatar_url = user.display_avatar.url

    await message.channel.send(f"User {user.display_name}: [Avatar]({avatar_url})")
