import discord
import io
from discord.ext import commands
import aiohttp


class Genshin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_data(self, uid: int):
        async with aiohttp.ClientSession() as session:
            data = await session.get(f"https://enka.network/api/uid/{uid}")
            return await data.json()

    @commands.command()
    async def damage(self, ctx: commands.Context, uid: int):
        # APIから情報を取得
        data = await self.get_data(uid)
        fp = io.StringIO(str(data))
        await ctx.reply(file=discord.File(fp))
        


async def setup(bot):
    await bot.add_cog(Genshin(bot))