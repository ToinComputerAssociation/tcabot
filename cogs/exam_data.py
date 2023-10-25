from discord.ext import commands
import discord
import aiomysql

class Examination(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def cog_load(self):
        self.pool = await aiomysql.create_pool(
            host=os.environ["MYSQL_HOST"], port=int(os.environ["MYSQL_PORT"]),
            user=os.environ["MYSQL_USERNAME"], password=os.environ["MYSQL_PASSWORD"],
            db=os.environ["MYSQL_DBNAME"], loop=self.loop, autocommit=True
        )
        pass

    @commands.command(aliases=["re"])
    async def register(self, ctx: commands.Context):
        await ctx.send("test!")

    @commands.command()
    async def view(self, ctx: commands.Context):
        await ctx.send("test2!")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Examination(bot))
