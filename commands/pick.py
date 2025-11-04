import random
name = "pick"
async def run(message, args):
    if len(args) < 1:
        await message.channel.send("Dùng cú pháp: $pick <tùy chọn 1>,<tùy chọn 2>")
        return
    text = " ".join(args)
    options = [opt.strip() for opt in text.split(",") if opt.strip()]    
    if len(options) < 2:
        await message.channel.send("phải nhập ít nhất 2 tùy chọn.")
        return
    choice = random.choice(options)
    await message.channel.send(f"{choice}")
