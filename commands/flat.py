name = "flat"

import io
import aiohttp
import discord
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

MAX_DIM = 1200
DEFAULT_INTENSITY = 20
MAX_INTENSITY = 100

async def fetch_image_bytes(url):
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(url, timeout=10) as r:
                if r.status == 200:
                    return await r.read()
    except:
        return None
    return None

async def get_avatar_bytes(member):
    for attr in ("display_avatar", "avatar", "avatar_url", "default_avatar"):
        try:
            v = getattr(member, attr)
            url = getattr(v, "url", None) or str(v)
            if url.startswith("http"):
                data = await fetch_image_bytes(url)
                if data:
                    return data
        except:
            continue
    return None

def flat_warp(img, intensity=20):
    img = img.convert("RGB")
    w, h = img.size

    fx = np.random.randn(h, w)
    fy = np.random.randn(h, w)

    fx = gaussian_filter(fx, sigma=25)
    fy = gaussian_filter(fy, sigma=25)

    fx = fx / np.max(np.abs(fx))
    fy = fy / np.max(np.abs(fy))

    amount = (intensity / 100) * min(w, h) * 0.35

    map_x = (np.tile(np.arange(w), (h, 1)) + fx * amount).clip(0, w - 1)
    map_y = (np.tile(np.arange(h)[:, None], (1, w)) + fy * amount).clip(0, h - 1)

    warped = np.zeros_like(np.array(img))
    src = np.array(img)

    warped[:, :, :] = src[map_y.astype(int), map_x.astype(int)]
    return Image.fromarray(warped)

def parse_intensity(parts):
    for p in parts:
        try:
            v = int(p)
            return max(0, min(MAX_INTENSITY, v))
        except:
            pass
    return DEFAULT_INTENSITY

async def run(message, args):
    if isinstance(args, str):
        parts = args.split()
    else:
        parts = args or []

    src_bytes = None
    for a in message.attachments:
        if any(a.filename.lower().endswith(ext) for ext in (".png",".jpg",".jpeg",".webp",".gif")):
            src_bytes = await fetch_image_bytes(a.url)
            break

    target = message.mentions[0] if message.mentions else message.author
    if not src_bytes:
        src_bytes = await get_avatar_bytes(target)

    if not src_bytes:
        return

    try:
        img = Image.open(io.BytesIO(src_bytes)).convert("RGB")
    except:
        return

    w, h = img.size
    if max(w, h) > MAX_DIM:
        scale = MAX_DIM / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)))

    intensity = parse_intensity(parts)

    try:
        out = flat_warp(img, intensity)
    except:
        return

    buf = io.BytesIO()
    out.save(buf, "PNG")
    buf.seek(0)

    await message.channel.send(file=discord.File(buf, "flat.png"))
