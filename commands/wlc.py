import discord
from discord.ext import commands
import json
import os

CONFIG_FILE = "welcome_config.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(data):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = load_config()

    @commands.command(name="setwlc")
    async def setwlc(self, ctx, channel: discord.TextChannel = None):
        """Chỉ định kênh welcome"""
        if not channel:
            await ctx.send("`$setwlc #ten-kenh`")
            return

        guild_id = str(ctx.guild.id)
        if guild_id not in self.config:
            self.config[guild_id] = {}

        self.config[guild_id]["channel"] = channel.id
        save_config(self.config)

        await ctx.send(f"welcom channel: {channel.mention}")

    @commands.command(name="settext")
    async def settext(self, ctx, *, text: str = None):
        """Đặt lời chào mừng"""
        if not text:
            await ctx.send("`!settext Chào {memberjoin}, bạn là thành viên thứ {membercount}`")
            return

        guild_id = str(ctx.guild.id)
        if guild_id not in self.config:
            self.config[guild_id] = {}

        self.config[guild_id]["text"] = text
        save_config(self.config)

        await ctx.send(f"welcom text: {text}")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_id = str(member.guild.id)
        cfg = self.config.get(guild_id)

        if not cfg or "channel" not in cfg or "text" not in cfg:
            return  

        channel = member.guild.get_channel(cfg["channel"])
        if not channel:
            return

        message = cfg["text"].replace("{memberjoin}", member.mention).replace("{membercount}", str(member.guild.member_count))
        await channel.send(message)


def setup(bot):
    bot.add_cog(Welcome(bot))
