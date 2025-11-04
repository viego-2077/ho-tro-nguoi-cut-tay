import os
import random

name = "tientri"

FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tientri.txt")

async def run(message, args):
    if not os.path.exists(FILE_PATH):
        await message.channel.send("Chưa có file `tientri.txt`.")
        return

    with open(FILE_PATH, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    if not lines:
        await message.channel.send("File `tientri.txt` trống.")
        return

    prophecy = random.choice(lines)
    await message.channel.send(f"🔮 **Lời tiên tri cho {message.author.display_name}:**\n{prophecy}")
