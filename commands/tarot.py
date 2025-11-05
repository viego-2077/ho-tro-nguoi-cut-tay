name = "tarot"

import random
import os
import discord

DECK = [
    ("0 - The Fool",
     "Khởi đầu mới, ngây thơ, phiêu lưu, mạo hiểm.",
     "Thiếu suy nghĩ, liều lĩnh, bắt đầu vội vàng."),
    ("I - The Magician",
     "Sử dụng tài nguyên, hiện thực hóa ý định, tự tin.",
     "Lãng phí tài năng, thao túng, mất cân bằng."),
    ("II - The High Priestess",
     "Trực giác, bí ẩn, đi vào nội tâm, trí tuệ tiềm ẩn.",
     "Bí ẩn quá mức, khó tiếp cận, che giấu thông tin."),
    ("III - The Empress",
     "Sự phong phú, nuôi dưỡng, sáng tạo, an toàn.",
     "Sự bám víu, lười biếng, thiếu ranh giới."),
    ("IV - The Emperor",
     "Quyền lực, cấu trúc, ổn định, trách nhiệm.",
     "Độc tài, cứng nhắc, lạm quyền."),
    ("V - The Hierophant",
     "Truyền thống, hướng dẫn, hệ thống niềm tin.",
     "Bảo thủ, chống đổi mới, lệ thuộc."),
    ("VI - The Lovers",
     "Tình yêu, lựa chọn có ý nghĩa, hòa hợp.",
     "Mâu thuẫn, lựa chọn sai, sự rạn nứt."),
    ("VII - The Chariot",
     "Ý chí mạnh mẽ, chiến thắng, tiến về phía trước.",
     "Mất kiểm soát, chống đối, thiếu hướng đi."),
    ("VIII - Strength",
     "Dũng cảm, kiên nhẫn, sức mạnh nội tâm.",
     "Sợ hãi, yếu đuối, thiếu lòng tự trọng."),
    ("IX - The Hermit",
     "Tìm kiếm chân lý, cô lập tích cực, khám phá nội tâm.",
     "Quá cô lập, lẩn tránh xã hội, cô đơn."),
    ("X - Wheel of Fortune",
     "Thay đổi, vận mệnh, chu kỳ mới.",
     "Kháng cự thay đổi, biến động khó lường."),
    ("XI - Justice",
     "Công bằng, trách nhiệm, sự thật được phơi bày.",
     "Thiếu công bằng, kết quả không công bằng."),
    ("XII - The Hanged Man",
     "Nhìn nhận khác, hy sinh, tạm dừng để suy nghĩ.",
     "Bế tắc, trì hoãn vô ích, từ bỏ sai cách."),
    ("XIII - Death",
     "Kết thúc dẫn đến tái sinh, chuyển hóa.",
     "Sợ thay đổi, chống đối quá mức, trì trệ."),
    ("XIV - Temperance",
     "Cân bằng, điều độ, kết hợp hài hòa.",
     "Thiếu điều độ, mất cân bằng, cực đoan."),
    ("XV - The Devil",
     "Ràng buộc, thói quen, dục vọng, học bài học.",
     "Giải phóng khỏi ràng buộc, nhận diện cạm bẫy."),
    ("XVI - The Tower",
     "Sụp đổ đột ngột, giải phóng, thức tỉnh.",
     "Khó khăn lớn, thay đổi đau đớn, mất nền tảng."),
    ("XVII - The Star",
     "Hy vọng, chữa lành, cảm hứng.",
     "Mất niềm tin, hy vọng bị lung lay."),
    ("XVIII - The Moon",
     "Trực giác, mơ mộng, những gì ẩn khuất.",
     "Ảo tưởng, lừa dối, hoang mang."),
    ("XIX - The Sun",
     "Thành công, niềm vui, sự rõ ràng.",
     "Thiếu khiêm tốn, hư vinh, thành công tạm thời."),
    ("XX - Judgement",
     "Phán xét, hồi sinh, nhận ra lời kêu gọi.",
     "Tự phán xét quá mức, trì hoãn quyết định."),
    ("XXI - The World",
     "Hoàn thành, viên mãn, chu kỳ trọn vẹn.",
     "Chưa hoàn thành, sợ kết thúc, trì hoãn bước tiếp.")
]

MAX_DRAW = 10
IMAGES_FOLDER = os.path.join("images", "tarot") 
VALID_EXTS = [".png", ".jpg", ".jpeg", ".webp"]

def draw_cards(n=1):
    """List các lá bài được rút"""
    n = max(1, min(n, MAX_DRAW))
    deck = list(enumerate(DECK))
    random.shuffle(deck)
    picks = []
    for i in range(n):
        idx, (name, up_text, rev_text) = deck[i]
        is_upright = random.random() > 0.30
        picks.append((idx, name, is_upright, up_text, rev_text))
    return picks


def find_image_for_card(index, name):
    """
    Tìm file ảnh
    """
    for ext in VALID_EXTS:
        p = os.path.join(IMAGES_FOLDER, f"{index}{ext}")
        if os.path.exists(p):
            return p
    slug = name.lower().replace(" ", "_").replace("-", "").replace("/", "_")
    import re
    slug = re.sub(r"[^a-z0-9_]", "", slug)
    for ext in VALID_EXTS:
        p = os.path.join(IMAGES_FOLDER, f"{slug}{ext}")
        if os.path.exists(p):
            return p
    return None

def format_single(card):
    idx, name, is_upright, up_text, rev_text = card
    orient = "🔆 Tích Cực" if is_upright else "🌑 Tiêu Cực"
    meaning = up_text if is_upright else rev_text
    return f"**{name}** ({orient})\n{meaning}"

def format_three(cards):
    labels = ["Past", "Present", "Future"]
    parts = []
    for label, card in zip(labels, cards):
        idx, name, is_upright, up_text, rev_text = card
        orient = "Upright" if is_upright else "Reversed"
        meaning = up_text if is_upright else rev_text
        parts.append(f"**{label} — {name}** ({orient})\n{meaning}")
    return "\n\n".join(parts)

async def run(message, args):
    n = 1
    if args:
        a0 = args[0].lower()
        if a0 == "shuffle":
            await message.channel.send("Deck shuffled.")
            return
        try:
            n = int(a0)
        except:
            n = 1

    if n < 1:
        n = 1
    if n > MAX_DRAW:
        await message.channel.send(f"Giới hạn tối đa là {MAX_DRAW} lá.")
        return

    picks = draw_cards(n)

    if n == 1:
        card = picks[0]
        text = format_single(card)
        img = find_image_for_card(card[0], card[1])
        if img:
            try:
                await message.channel.send(text)
                await message.channel.send(file=discord.File(img))
            except Exception:
                await message.channel.send(text)
        else:
            await message.channel.send(text)
        return

    if n == 3:
        text = format_three(picks)
        await message.channel.send(text)
        for card in picks:
            img = find_image_for_card(card[0], card[1])
            if img:
                try:
                    await message.channel.send(file=discord.File(img))
                except Exception:
                    pass
        return

    parts = []
    for idx, card in enumerate(picks, start=1):
        i, name, is_upright, up_text, rev_text = card
        orient = "Upright" if is_upright else "Reversed"
        meaning = up_text if is_upright else rev_text
        parts.append(f"**{idx}. {name}** ({orient})\n{meaning}")
    await message.channel.send("\n\n".join(parts))

    for card in picks:
        img = find_image_for_card(card[0], card[1])
        if img:
            try:
                await message.channel.send(file=discord.File(img))
            except Exception:
                pass
