name = "rat"

import os
import io
import aiohttp
from PIL import Image, ImageDraw, ImageOps
import discord

BG_PATH = os.path.join("images", "fun_images", "rat.png")

async def fetch_image_bytes(url, timeout=15):
    headers = {"User-Agent": "RatBot/1.0"}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=timeout, headers=headers) as resp:
                if resp.status == 200:
                    return await resp.read()
    except Exception:
        return None
    return None

def circle_crop_from_bytes(data, size):
    im = Image.open(io.BytesIO(data)).convert("RGBA")
    im = im.resize((size, size), Image.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse((0, 0, size, size), fill=255)
    im.putalpha(mask)
    return im

async def get_member_avatar_image(member, size):
    candidates = []
    try:
        da = getattr(member, "display_avatar", None)
        if da:
            url = getattr(da, "url", None) or str(da)
            if url and url.startswith("http"):
                candidates.append(url)
    except Exception:
        pass
    try:
        av = getattr(member, "avatar", None)
        if av:
            url = getattr(av, "url", None) or str(av)
            if url and url.startswith("http"):
                candidates.append(url)
    except Exception:
        pass
    try:
        au = getattr(member, "avatar_url", None)
        if au:
            url = str(au)
            if url and url.startswith("http"):
                candidates.append(url)
    except Exception:
        pass
    try:
        daf = getattr(member, "default_avatar", None)
        if daf:
            url = getattr(daf, "url", None) or str(daf)
            if url and url.startswith("http"):
                candidates.append(url)
    except Exception:
        pass

    seen = set()
    filtered = []
    for c in candidates:
        if c and c not in seen:
            seen.add(c)
            filtered.append(c)

    for url in filtered:
        data = await fetch_image_bytes(url)
        if data:
            try:
                return circle_crop_from_bytes(data, size)
            except Exception:
                continue

    return Image.new("RGBA", (size, size), (150, 150, 150, 255))

def add_border_circle(im, border_size=8, border_color=(255,255,255,255)):
    w, h = im.size
    out = Image.new("RGBA", (w + border_size*2, h + border_size*2), (0,0,0,0))
    mask = Image.new("L", out.size, 0)
    d = ImageDraw.Draw(mask)
    d.ellipse((0,0,out.width-1,out.height-1), fill=255)
    border_layer = Image.new("RGBA", out.size, border_color)
    out.paste(border_layer, (0,0), mask)
    out.paste(im, (border_size, border_size), im)
    return out

async def run(message, args):
    author = message.author
    target = None
    if getattr(message, "mentions", None):
        if message.mentions:
            target = message.mentions[0]
    if target is None:
        try:
            ref = getattr(message, "reference", None) or getattr(message, "message_reference", None)
            if ref and getattr(ref, "resolved", None):
                target = ref.resolved.author
        except Exception:
            target = None
    if target is None:
        target = author

    if not os.path.exists(BG_PATH):
        try:
            await message.channel.send("Background image not found (images/fun_images/rat.png).")
        except Exception:
            pass
        return

    try:
        bg = Image.open(BG_PATH).convert("RGBA")
    except Exception:
        try:
            await message.channel.send("Không thể mở background rat.png.")
        except Exception:
            pass
        return

    W, H = bg.size

    base_avatar_ratio = 0.28
    dx_pct = 50  
    dy_pct = 36
    scale = 0.6
    rot = -6.0
    if args:
        if isinstance(args, str):
            parts = args.strip().split()
        else:
            parts = args
        try:
            if len(parts) >= 1:
                dx_pct = float(parts[0])
            if len(parts) >= 2:
                dy_pct = float(parts[1])
            if len(parts) >= 3:
                scale = float(parts[2])
            if len(parts) >= 4:
                rot = float(parts[3])
        except Exception:
            pass

    avatar_size = int(min(W, H) * base_avatar_ratio * scale)
    avatar_size = max(40, avatar_size)

    av_im = await get_member_avatar_image(target, avatar_size)

    framed = add_border_circle(av_im, border_size=max(6, avatar_size//20), border_color=(255,255,255,255))
    if rot:
        try:
            framed = framed.rotate(rot, resample=Image.BICUBIC, expand=False)
        except Exception:
            pass

    paste_x = int(W * (dx_pct / 100.0)) - framed.width//2
    paste_y = int(H * (dy_pct / 100.0)) - framed.height//2

    paste_x = max(0, min(paste_x, W - framed.width))
    paste_y = max(0, min(paste_y, H - framed.height))

    out = bg.copy()
    out.paste(framed, (paste_x, paste_y), framed)

    buf = io.BytesIO()
    out.save(buf, "PNG")
    buf.seek(0)
    try:
        await message.channel.send(file=discord.File(buf, "rat.png"))
    except Exception:
        try:
            await message.channel.send("Failed to send image.")
        except Exception:
            pass
