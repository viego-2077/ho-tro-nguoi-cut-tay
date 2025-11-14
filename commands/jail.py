name = "jail"

import io
import os
import aiohttp
from PIL import Image, ImageOps
import discord

JAIL_PATH = "images/fun_images/jail.png"

OUT_SIZE = 512

async def fetch_image_bytes(url, timeout=10, headers=None):
    """Tải raw bytes từ URL, trả None nếu thất bại."""
    headers = headers or {"User-Agent": "Mozilla/5.0 (compatible)"}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=timeout, headers=headers) as resp:
                if resp.status == 200:
                    return await resp.read()
    except Exception:
        return None
    return None

async def get_avatar_image(member, size=OUT_SIZE):
    """
    Image (RGBA)
    """
    candidates = []
    for attr in ("display_avatar", "avatar", "avatar_url", "default_avatar"):
        try:
            val = getattr(member, attr, None)
            if val:
                url = getattr(val, "url", None) or str(val)
                if url and url.startswith("http"):
                    candidates.append(url)
        except Exception:
            continue

    seen = set()
    filtered = []
    for u in candidates:
        if u not in seen:
            seen.add(u)
            filtered.append(u)

    for url in filtered:
        data = await fetch_image_bytes(url)
        if data:
            try:
                im = Image.open(io.BytesIO(data)).convert("RGBA")
                return im.resize((size, size), Image.LANCZOS)
            except Exception:
                continue

    return Image.new("RGBA", (size, size), (120, 120, 120, 255))

def rounded_crop(im: Image.Image, radius=40):
    """Cắt bo góc cho avatar"""
    im = im.convert("RGBA")
    mask = Image.new("L", im.size, 0)
    d = Image.new("L", im.size)
    from PIL import ImageDraw
    draw = ImageDraw.Draw(mask)
    w, h = im.size
    draw.rounded_rectangle((0,0,w,h), radius=radius, fill=255)
    out = Image.new("RGBA", im.size, (0,0,0,0))
    out.paste(im, (0,0), mask)
    return out

async def run(message, args):
    """
    Usage:
      ,jail           -> jail chính bạn
      ,jail @user     -> jail người được mention
    """
    target = None
    try:
        mentions = getattr(message, "mentions", None) or []
        if mentions:
            target = mentions[0]
        else:
            target = message.author
    except Exception:
        target = message.author

    if not os.path.exists(JAIL_PATH):
        await message.channel.send("error jail overlay (images/jail/jail.png).")
        return

    try:
        avatar_im = await get_avatar_image(target, size=OUT_SIZE)
    except Exception:
        avatar_im = Image.new("RGBA", (OUT_SIZE, OUT_SIZE), (120,120,120,255))

    try:
        avatar_im = rounded_crop(avatar_im, radius=48)
    except Exception:
        pass

    try:
        jail_overlay = Image.open(JAIL_PATH).convert("RGBA").resize((OUT_SIZE, OUT_SIZE), Image.LANCZOS)
    except Exception:
        await message.channel.send("error jail overlay.")
        return

    canvas = Image.new("RGBA", (OUT_SIZE, OUT_SIZE), (30,30,30,255))
    canvas.paste(avatar_im, (0,0), avatar_im)
    canvas.paste(jail_overlay, (0,0), jail_overlay)

    buf = io.BytesIO()
    canvas.save(buf, "PNG")
    buf.seek(0)

    try:
        await message.channel.send(f"**{getattr(target, 'display_name', str(target))} đã bị tống giam!**", file=discord.File(buf, "jail.png"))
    except Exception as e:
        try:
            await message.channel.send(file=discord.File(buf, "jail.png"))
        except Exception:
            pass
