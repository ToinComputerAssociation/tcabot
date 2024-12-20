from discord.ext import commands
import datetime
import time
from ._hidden_data import TCA_MEMBERS, FORM_URL


class Work(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def form(self, ctx: commands.Context, type = "0"):
        if type not in ["0", "1"]:
            return await ctx.send("タイプは 0(活動開始) か 1(活動終了) のどちらかにしてください。")
        if ctx.author.id not in TCA_MEMBERS:
            return await ctx.send("TCAメンバー一覧データの中にあなたが見つかりませんでした。")
        await ctx.send(FORM_URL.format(
            mode=["活動開始", "活動終了"][int(type)], user=TCA_MEMBERS[ctx.author.id],
            date=datetime.date.today().isoformat(), now=time.strftime("%H:%M")
        ))  # urlの送信

    @commands.command()
    @commands.is_owner()
    async def add_syafu(self, ctx: commands.Context):
        emoji = self.bot.get_guild(1107217216203665420).get_emoji(1266237861905305732)
        data = await emoji.read()
        new = await ctx.guild.create_custom_emoji(name="syafu", image=data, reason="社不コマンド")
        await ctx.send(f"<:syafu:{new.id}>")

    @commands.command()
    @commands.is_owner()
    async def add_syateki(self, ctx: commands.Context):
        emoji = self.bot.get_guild(1107217216203665420).get_emoji(1298439548879241276)
        data = await emoji.read()
        new = await ctx.guild.create_custom_emoji(name="syateki", image=data, reason="社適コマンド")
        await ctx.send(f"<:syateki:{new.id}>")

async def setup(bot):
    await bot.add_cog(Work(bot))