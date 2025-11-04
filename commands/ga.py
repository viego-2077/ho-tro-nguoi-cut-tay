import asyncio
from datetime import datetime, timedelta

name = "ga"

async def run(message, args):
    if len(args) < 3:
        await message.channel.send("`$ga <số_giải> <thời_gian> <phần_thưởng>`\nVí dụ: `$ga 1 1h30m Nitro Boost`")
        return

    reward = args[0]
    try:
        winners_count = int(args[0])
    except ValueError:
        await message.channel.send("Số lượng người thắng không hợp lệ.")
        return

    time_str = args[1].lower()
    reward = " ".join(args[2:])


    seconds = 0
    num = ''
    for ch in time_str:
        if ch.isdigit():
            num += ch
        elif ch in ['s', 'm', 'h', 'd']:
            if num:
                val = int(num)
                if ch == 's':
                    seconds += val
                elif ch == 'm':
                    seconds += val * 60
                elif ch == 'h':
                    seconds += val * 3600
                elif ch == 'd':
                    seconds += val * 86400
                num = ''
    if seconds == 0:
        await message.channel.send("Thời gian không hợp lệ. Ví dụ: `10s`, `5m`, `1h30m`, `1d`")
        return

    end_time = datetime.now() + timedelta(seconds=seconds)
    formatted_end = end_time.strftime("%H:%M:%S")

    msg = await message.channel.send(
        f"# 🎉 **GIVEAWAY** 🎉\n"
        f"> **Phần thưởng:** {reward}\n"
        f"> **Số giải thưởng:** {winners_count}\n"
        f"> **Kết thúc lúc:** {formatted_end}\n"
        f"> **Người tạo:** {message.author.mention}\n"
    )

    await msg.add_reaction("🎉")

    await asyncio.sleep(seconds)

    msg = await message.channel.fetch_message(msg.id)
    users = [user async for user in msg.reactions[0].users()]

    users = [u for u in users if not u.bot and u.id != 1430744883932430389]

    if len(users) == 0:
        await message.channel.send("Không có ai tham gia giveaway.")
        return

    import random
    winners = random.sample(users, min(winners_count, len(users)))

    winner_mentions = ", ".join([w.mention for w in winners])
    await message.channel.send(
        f"# Giveaway kết thúc! 🎊\n"
        f"**🎁 Phần thưởng: {reward}**\n"
        f"**🏆 Người thắng: {winner_mentions}**"
    )
