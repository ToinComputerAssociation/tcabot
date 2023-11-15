import os
import discord
from discord.ext import commands


class MyCog(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        if "PROBLEMS_TOKEN" not in os.environ:
            raise ValueError("there is no atcoder_problems token")
        self.token = os.environ["PROBLEMS_TOKEN"]


async def setup(bot):
    await bot.add_cog(MyCog(bot))
