from discord.ext import commands
import discord
import aiomysql
import os


class TestType(discord.ui.Select):
    def __init__(self, default=None):
        super().__init__(
            placeholder="テスト種別を選択...",
            options=[
                discord.SelectOption(label="前期中間", value="1", default=default==1),
                discord.SelectOption(label="前期期末", value="2", default=default==2),
                discord.SelectOption(label="後期中間", value="3", default=default==3),
                discord.SelectOption(label="後期期末", value="4", default=default==4)
            ]
        )

    async def callback(self, interaction):
        selected = int(self.values[0])
        # self.view.add_item()
        await interaction.response.edit_message(
            content=f"selected {selected}", view=self.view
        )


class Grade(discord.ui.Select):
    def __init__(self, default=None):
        super().__init__(
            placeholder="学年を選択...",
            options=[
                discord.SelectOption(label="1年生", value="1", default=default==1),
                discord.SelectOption(label="2年生", value="2", default=default==2),
                discord.SelectOption(label="3年生", value="3", default=default==3)
            ]
        )

    async def callback(self, interaction):
        selected = int(self.values[0])
        # self.view.add_item()
        await interaction.response.edit_message(
            content=f"selected {selected}", view=self.view
        )


class Examination(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def cog_load(self):
        self.pool = await aiomysql.create_pool(
            host=os.environ["MYSQL_HOST"], port=int(os.environ["MYSQL_PORT"]),
            user=os.environ["MYSQL_USERNAME"], password=os.environ["MYSQL_PASSWORD"],
            db=os.environ["MYSQL_DBNAME"], loop=self.bot.loop, autocommit=True
        )

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
        view.add_item(Grade())
        view.add_item(TestType())
        await ctx.send("test!", view=view)

    @commands.hybrid_command()
    async def view(self, ctx: commands.Context):
        await ctx.send("test2!")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Examination(bot))
