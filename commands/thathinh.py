name = "thathinh"

import aiohttp
import discord

PICKUP_API = "https://api.popcat.xyz/pickuplines"
TRANS_API = "https://api.mymemory.translated.net/get"

async def run(message, args):
    async with aiohttp.ClientSession() as session:
        async with session.get(PICKUP_API) as resp:
            if resp.status != 200:
                await message.channel.send("Error Pickup API.")
                return
            data = await resp.json(content_type=None)

        pickup_line = data.get("pickupline") or data.get("pickup") or data.get("line")

        if not pickup_line:
            await message.channel.send("😢 No pickup line today.")
            return

        params = {"q": pickup_line, "langpair": "en|vi"}
        async with session.get(TRANS_API, params=params) as t:
            trans_data = await t.json()
            vi_text = trans_data.get("responseData", {}).get("translatedText")

        if not vi_text:
            await message.channel.send(f"{pickup_line}")
            return

        await message.channel.send(f"{vi_text}")
