from discord.ext import commands
import discord
import aiomysql
import os


class Sel(discord.ui.Select):
    def __init__(self):
        super().__init__(options=[discord.SelectOption(label="test", value="test")])

    async def callback(self, interaction):
        await interaction.response.send_message(str(self.values))


class Examination(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def cog_load(self):
        self.pool = await aiomysql.create_pool(
            host=os.environ["MYSQL_HOST"], port=int(os.environ["MYSQL_PORT"]),
            user=os.environ["MYSQL_USERNAME"], password=os.environ["MYSQL_PASSWORD"],
            db=os.environ["MYSQL_DBNAME"], loop=self.bot.loop, autocommit=True
        )
        pass

    async def execute_sql(
        self, sql: str, _injects: tuple | None = None, _return_type = ""
    ) -> tuple:
        "SQL文を実行します。"
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(sql, _injects)
                if _return_type == "fetchone":
                    return await cursor.fetchone()
                else:
                    return await cursor.fetchall()

    @commands.hybrid_command(aliases=["re"])
    async def register(self, ctx: commands.Context):
        view = discord.ui.View()
        view.add_item(Sel())
        await ctx.send("test!", view=view)

    @commands.hybrid_command()
    async def view(self, ctx: commands.Context):
        await ctx.send("test2!")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Examination(bot))
