import discord
import json
import os
import importlib.util
import asyncio


with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

OWNER_ID = config["owner_id"]
PREFIX = config["prefix"]


with open("tokens.txt", "r", encoding="utf-8") as f:
    TOKENS = [line.strip() for line in f if line.strip()]



def load_commands():
    commands = {}
    if not os.path.exists("commands"):
        os.makedirs("commands")

    for filename in os.listdir("commands"):
        if not filename.endswith(".py"):
            continue
        filepath = os.path.join("commands", filename)

        try:
            spec = importlib.util.spec_from_file_location(filename[:-3], filepath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            
            cmd_name = getattr(module, "name", None)
            if not cmd_name:
                print(f"File '{filename}' không có biến 'name' — bỏ qua.")
                continue

            commands[cmd_name.lower()] = module
            print(f"Đã nạp lệnh: {cmd_name}")

        except Exception as e:
            print(f"Lỗi khi nạp file '{filename}': {e}")

    print(f"Tổng cộng {len(commands)} lệnh được nạp.")
    return commands


COMMANDS = load_commands()



class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.COMMANDS = COMMANDS

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")

    async def on_message(self, message):
        if message.author.id == self.user.id:
            return

       
        if message.content.startswith(PREFIX):
            parts = message.content[len(PREFIX):].split()
            if not parts:
                return

            cmd_name = parts[0].lower()
            args = parts[1:]

            if cmd_name in self.COMMANDS:
                try:
                    await self.COMMANDS[cmd_name].run(message, args)
                except Exception as e:
                    await message.channel.send(f"⚠️ Lỗi khi chạy `{cmd_name}`: {e}")
                    print(f"error {cmd_name}: {e}")
            else:
                
                all_cmds = ", ".join(self.COMMANDS.keys())
                await message.channel.send(f"Lệnh `{cmd_name}` không tồn tại.\n📜 Lệnh có sẵn: {all_cmds}")



async def start_all_bots():
    clients = []
    for token in TOKENS:
        client = MyClient()
        clients.append(client)
        asyncio.create_task(client.start(token))

    while True:
        await asyncio.sleep(3600)


import json
import os

AUTO_FILE = "auto_responses.json"

def load_auto_responses():
    if not os.path.exists(AUTO_FILE):
        return []
    try:
        with open(AUTO_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

_original_on_message = getattr(MyClient, "on_message", None)

async def _patched_on_message(self, message):
    if _original_on_message is not None:
        try:
            await _original_on_message(self, message)
        except Exception:
            pass

    try:
        if message.author.id == self.user.id:
            return
    except Exception:
        return

    try:
        if isinstance(message.content, str) and message.content.startswith(PREFIX):
            return
    except Exception:
        pass

    responses = load_auto_responses()
    if not responses:
        return

    guild_id = str(message.guild.id) if message.guild else None
    content = (message.content or "").strip().lower()

    for entry in responses:
        try:
            if entry.get("guild_id") != guild_id:
                continue
            trigger = (entry.get("trigger") or "").strip().lower()
            resp = entry.get("response") or ""
            if not trigger:
                continue
            if content == trigger:
                try:
                    await message.reply(resp)
                except Exception:
                    try:
                        await message.channel.send(resp)
                    except Exception:
                        pass
                break
        except Exception:
            continue
MyClient.on_message = _patched_on_message
        
if __name__ == "__main__":
    asyncio.run(start_all_bots())