import os
import discord
import datetime
from discord.ext import commands, tasks


class MyCog(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        if "PROBLEMS_TOKEN" not in os.environ:
            raise ValueError("there is no atcoder_problems token")
        self.token = os.environ["PROBLEMS_TOKEN"]
        self.create_bacha.start()

    def cog_unload(self):
        self.create_bacha.cancel()

    @tasks.loop(time=datetime.time(7, 30, 0))
    async def create_bacha(self):
        pass

async def setup(bot):
    await bot.add_cog(MyCog(bot))
