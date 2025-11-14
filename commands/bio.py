name = "bio"

import os
import io
import re
import json
import aiohttp
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from urllib.parse import urlparse, urlunparse


DATA_PATH = "data/bios.json"
IMAGE_OUT_DIR = "images/bio"

BG_DEFAULT_PATH = os.path.join(IMAGE_OUT_DIR, "biocard.png")

ICON_DEFAULT_PATH = os.path.join(IMAGE_OUT_DIR, "icon.png")

FONT_PATHS = [
    "arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
]

W, H = 1000, 520

MAX_BG_BYTES = 25 * 1024 * 1024

BIO_FIELDS = [
    ("ten", "Tên"),
    ("bietdanh", "Biệt danh"),
    ("ngaysinh", "Ngày sinh"),
    ("noio", "Nơi ở"),
    ("sothich", "Sở thích"),
    ("mqh", "MQH")
]


def ensure_dirs():
    """Đảm bảo thư mục data/ và images/bio/ tồn tại."""
    os.makedirs(os.path.dirname(DATA_PATH) or ".", exist_ok=True)
    os.makedirs(IMAGE_OUT_DIR, exist_ok=True)

def ensure_datafile():
    """create bios.json"""
    ensure_dirs()
    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=2)

def read_bios():
    ensure_datafile()
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def write_bios(data):
    ensure_datafile()
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_font(size):
    """Load font"""
    for p in FONT_PATHS:
        try:
            return ImageFont.truetype(p, size)
        except:
            continue
    return ImageFont.load_default()

def measure_text(draw, text, font):
    """calculate text (cross-version compatible)."""
    if hasattr(draw, "textbbox"):
        bbox = draw.textbbox((0,0), text, font=font)
        return bbox[2]-bbox[0], bbox[3]-bbox[1]
    return draw.textsize(text, font=font)

def rounded_square_crop(im, size, radius=24):
    """Cắt avatar thành hình vuông bo góc."""
    im = im.resize((size, size)).convert("RGBA")
    mask = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle((0, 0, size, size), radius=radius, fill=255)
    im.putalpha(mask)
    return im

def normalize_url_strip_query(url: str) -> str:
    """Xoá query"""
    try:
        p = urlparse(url)
        if any(x in p.netloc for x in (
            "discordapp.com", "discord.com",
            "media.discordapp.net", "cdn.discordapp.com"
        )):
            p2 = p._replace(query="", fragment="")
            return urlunparse(p2)
    except:
        pass
    return url

async def fetch_image_raw(url, timeout=10, headers=None):
    """Fetch ảnh từ URL."""
    headers = headers or {"User-Agent": "Mozilla/5.0 (compatible)"}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                timeout=timeout,
                headers=headers,
                allow_redirects=True
            ) as resp:
                data = await resp.read()
                if resp.status == 200 and data:
                    return data
    except:
        pass
    return None

async def try_fetch_bg(url):
    """
    3 step Fetch picture from URL:
    """
    if not url:
        return None

    data = await fetch_image_raw(url)
    if data:
        return data

    stripped = normalize_url_strip_query(url)
    if stripped != url:
        data = await fetch_image_raw(stripped)
        if data:
            return data

    try:
        p = urlparse(url)
        referer = f"{p.scheme}://{p.netloc}/"
    except:
        referer = None

    if referer:
        data = await fetch_image_raw(
            stripped or url,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Referer": referer
            }
        )
        if data:
            return data

    return None


def save_bg_local(uid: str, img_bytes: bytes):
    """Load background image and save to PNG images/bio/bg_<uid>.png."""
    try:
        im = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
        path = os.path.join(IMAGE_OUT_DIR, f"bg_{uid}.png")
        im.save(path, "PNG")
        return path
    except:
        return None

def remove_local_bg(path):
    """Delete local background."""
    try:
        if path and os.path.exists(path):
            os.remove(path)
            return True
    except:
        pass
    return False


def load_icon_img(size):
    """Load icon mặc định từ file icon.png nếu có."""
    if os.path.exists(ICON_DEFAULT_PATH):
        try:
            return Image.open(ICON_DEFAULT_PATH).convert("RGBA").resize((size, size))
        except:
            return None
    return None


async def fetch_avatar(member, size):
    """
    Get avatar from member | PIL Image.
    """
    candidates = []
    for attr in ["display_avatar", "avatar", "avatar_url", "default_avatar"]:
        try:
            val = getattr(member, attr, None)
            if val:
                url = getattr(val, "url", None) or str(val)
                if url.startswith("http"):
                    candidates.append(url)
        except:
            continue

    for url in candidates:
        data = await fetch_image_raw(url)
        if data:
            try:
                im = Image.open(io.BytesIO(data)).convert("RGBA")
                return im.resize((size, size))
            except:
                continue

    return Image.new("RGBA", (size, size), (120,120,120,255))


async def get_attachment_image_bytes(message):
    """
    Get picture bytes from message attachments if any.
    """
    try:
        attachments = getattr(message, "attachments", None) or []
        if not attachments:
            return None

        for a in attachments:
            ctype = getattr(a, "content_type", None)
            fname = getattr(a, "filename", "") or ""
            url = getattr(a, "url", None) or getattr(a, "proxy_url", None)

            if ctype and ctype.startswith("image"):
                return await fetch_image_raw(url)

            if any(fname.lower().endswith(ext) for ext in (
                ".png", ".jpg", ".jpeg", ".webp", ".gif"
            )):
                return await fetch_image_raw(url)

        return None
    except:
        return None

async def run(message, args):
    """
    Xử lý lệnh:
    """

    if isinstance(args, str):
        parts = args.strip().split()
    else:
        parts = args or []

    ensure_dirs()

    author = message.author
    mentions = getattr(message, "mentions", []) or []
    target = mentions[0] if mentions else author

    if len(parts) >= 1 and parts[0].lower() == "help":
        help_text = (
            "**BIO CARD HELP**\n"
            "`,bio` → Xem bio của bạn.\n"
            "`,bio @user` → Xem bio của người khác.\n"
            "`,bio edit <field> <value>` → Sửa thông tin.\n"
            "`,bio edit bg <link>` → Đặt ảnh nền (có thể gửi ảnh kèm theo).\n"
            "`,bio edit icon <emoji>` → Đặt icon riêng.\n"
            "`,bio reset bg` → Xoá nền riêng.\n"
            "`,bio reset icon` → Xoá icon riêng.\n"
            "`,bio delete` → Xoá toàn bộ bio.\n"
        )
        await message.channel.send(help_text)
        return

    if len(parts) >= 1 and parts[0].lower() == "edit":
        if len(parts) < 2:
            await message.channel.send("Cách dùng: `,bio edit <field> <value>` hoặc `$bio edit bg <link>`.")
            return

        field = parts[1].lower()
        value = " ".join(parts[2:]).strip() if len(parts) >= 3 else ""

        bios = read_bios()
        uid = str(author.id)
        entry = bios.get(uid, {})

        if field == "bg":

            att_bytes = await get_attachment_image_bytes(message)

            if att_bytes:
                bg_bytes = att_bytes
                source = "attachment"
            else:
                if not value:
                    await message.channel.send("Hãy gửi link ảnh hoặc đính kèm ảnh.")
                    return

                if not (value.startswith("http://") or value.startswith("https://")):
                    await message.channel.send("Link ảnh không hợp lệ.")
                    return

                bg_bytes = await try_fetch_bg(value)
                source = "link"

            if not bg_bytes:
                await message.channel.send("Không tải được ảnh nền.")
                return

            if len(bg_bytes) > MAX_BG_BYTES:
                await message.channel.send(f"Ảnh quá lớn (> {MAX_BG_BYTES//1024//1024}MB).")
                return

            saved_path = save_bg_local(uid, bg_bytes)
            if not saved_path:
                await message.channel.send("Không lưu được ảnh.")
                return

            if source == "link":
                entry["bg"] = normalize_url_strip_query(value)
            else:
                entry.pop("bg", None)

            entry["bg_local"] = saved_path
            entry["updatedAt"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            entry["authorTag"] = str(author)

            bios[uid] = entry
            write_bios(bios)

            await message.channel.send(f"Update bg from {source}.")
            return

        if field == "icon":
            m = re.search(r"<a?:\w+:(\d+)>", value)
            if m:
                emoji_id = m.group(1)
                ext = "gif" if value.startswith("<a:") else "png"
                entry["icon_url"] = f"https://cdn.discordapp.com/emojis/{emoji_id}.{ext}?size=64&quality=lossless"
                entry.pop("icon_unicode", None)
            else:
                entry["icon_unicode"] = value
                entry.pop("icon_url", None)

            entry["updatedAt"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            entry["authorTag"] = str(author)

            bios[uid] = entry
            write_bios(bios)
            await message.channel.send("Update custom icon.")
            return

        allowed = [k for k,_ in BIO_FIELDS]
        if field not in allowed:
            await message.channel.send("Field không hợp lệ.")
            return

        entry[field] = value
        entry["updatedAt"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        entry["authorTag"] = str(author)

        bios[uid] = entry
        write_bios(bios)

        await message.channel.send(f"Update **{field}** = {value}")
        return

    if len(parts) >= 2 and parts[0].lower() == "reset":
        sub = parts[1].lower()

        bios = read_bios()
        uid = str(author.id)
        entry = bios.get(uid, {})

        if sub == "bg":
            removed = False

            if "bg_local" in entry:
                path = entry.pop("bg_local")
                remove_local_bg(path)
                removed = True

            if "bg" in entry:
                entry.pop("bg")
                removed = True

            if removed:
                bios[uid] = entry
                write_bios(bios)
                await message.channel.send("Reset background.")
            else:
                await message.channel.send("No custom background.")
            return

        if sub == "icon":
            changed = False
            if "icon_url" in entry:
                entry.pop("icon_url"); changed = True
            if "icon_unicode" in entry:
                entry.pop("icon_unicode"); changed = True

            if changed:
                bios[uid] = entry
                write_bios(bios)
                await message.channel.send("reset custom icon.")
            else:
                await message.channel.send("No custom icon.")
            return

    if len(parts) >= 1 and parts[0].lower() == "delete":
        bios = read_bios()
        uid = str(author.id)

        if uid in bios:
            entry = bios.pop(uid)

            if entry.get("bg_local"):
                remove_local_bg(entry["bg_local"])

            write_bios(bios)
            await message.channel.send("Delete bio.")
        else:
            await message.channel.send("No bio.")
        return


    bios = read_bios()
    info = bios.get(str(target.id), {})

    canvas = None

    if info.get("bg_local") and os.path.exists(info["bg_local"]):
        try:
            bg = Image.open(info["bg_local"]).convert("RGBA").resize((W, H))
            canvas = bg.copy()
        except:
            canvas = None

    if canvas is None:
        url = info.get("bg")
        bg_bytes = None
        if url:
            bg_bytes = await try_fetch_bg(url)
        if bg_bytes:
            try:
                bg = Image.open(io.BytesIO(bg_bytes)).convert("RGBA").resize((W, H))
                canvas = bg.copy()
            except:
                canvas = None

    if canvas is None:
        if os.path.exists(BG_DEFAULT_PATH):
            try:
                bg = Image.open(BG_DEFAULT_PATH).convert("RGBA").resize((W, H))
                canvas = bg.copy()
            except:
                canvas = Image.new("RGBA", (W, H), (40,40,40,255))
        else:
            canvas = Image.new("RGBA", (W, H), (40,40,40,255))

    draw = ImageDraw.Draw(canvas)

    title_font = get_font(56)
    draw.text((38, 22), "BIO CARD", font=title_font, fill=(0,0,0,140))
    draw.text((36, 20), "BIO CARD", font=title_font, fill=(255,255,255,255))

    icon_size = 28
    icon_img = None

    if info.get("icon_url"):
        data = await try_fetch_bg(info["icon_url"])
        if data:
            try:
                icon_img = Image.open(io.BytesIO(data)).convert("RGBA").resize((icon_size, icon_size))
            except:
                icon_img = None

    icon_unicode = info.get("icon_unicode")

    if not icon_img and not icon_unicode:
        icon_img = load_icon_img(icon_size)

    left_x = 36
    y = 120
    gap = 52

    label_font = get_font(28)
    value_font = get_font(30)

    for key, label in BIO_FIELDS:
        label_text = f"{label}:"

        if icon_img:
            canvas.paste(icon_img, (left_x, y), icon_img)
            lbl_x = left_x + icon_size + 10

        elif icon_unicode:
            draw.text((left_x, y), icon_unicode, font=get_font(30), fill=(255,255,255,255))
            lbl_x = left_x + 36

        else:
            lbl_x = left_x

        draw.text((lbl_x, y), label_text, font=label_font, fill=(255,230,160,255))

        lbl_w, _ = measure_text(draw, label_text, label_font)

        val = info.get(key) or "Chưa rõ"
        draw.text((lbl_x + lbl_w + 12, y), str(val), font=value_font, fill=(255,255,255,255))

        y += gap

    small_font = get_font(18)
    meta = info.get("updatedAt")
    meta_text = (
        f"Updated: {meta} • By: {info.get('authorTag','Chưa rõ')}"
        if meta else
        "Dùng `,bio help` để sửa thông tin."
    )
    draw.text((left_x, H - 40), meta_text, font=small_font, fill=(180,180,180,200))

    avatar_size = 180
    av = await fetch_avatar(target, avatar_size)
    avr = rounded_square_crop(av, avatar_size, radius=28)

    border = 8
    out_av = Image.new("RGBA", (avatar_size + border*2, avatar_size + border*2), (0,0,0,0))

    dd = ImageDraw.Draw(out_av)
    dd.rounded_rectangle((0,0,out_av.width-1,out_av.height-1), radius=36, fill=(255,182,193,255))

    out_av.paste(avr, (border,border), avr)

    x_av = W - out_av.width - 36
    y_av = 20

    canvas.paste(out_av, (x_av, y_av), out_av)

    name_font = get_font(26)
    name_text = getattr(target, "display_name", str(target))
    nw, _ = measure_text(draw, name_text, name_font)
    draw.text((x_av + out_av.width//2 - nw//2, y_av + out_av.height + 8),
              name_text,
              font=name_font,
              fill=(255,255,255,255))

    bio_buffer = io.BytesIO()
    canvas.save(bio_buffer, format="PNG")
    bio_buffer.seek(0)

    import discord as _discord
    await message.channel.send(file=_discord.File(bio_buffer, "biocard_render.png"))

