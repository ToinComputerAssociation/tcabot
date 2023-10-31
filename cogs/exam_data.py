from typing import Optional
from discord.ext import commands
import discord
import aiomysql
import os


class DataCreateView(discord.ui.View):
    def __init__(self, bot):
        super().__init__()
        self.add_item(Grade())
        self.add_item(TestType())
        self.add_item(SubmitButton(1))
        self.bot = bot

    def get_item(self, cls):
        for i in self.children:
            if isinstance(i, cls):
                return i
        raise KeyError("The class %r not found." % cls)


class TestType(discord.ui.Select):
    def __init__(self):
        super().__init__(
            placeholder="テスト種別を選択...",
            options=[
                discord.SelectOption(label="前期中間", value="1"),
                discord.SelectOption(label="前期期末", value="2"),
                discord.SelectOption(label="後期中間", value="3"),
                discord.SelectOption(label="後期期末", value="4")
            ]
        )

    async def callback(self, interaction):
        selected = int(self.values[0])
        for i in range(4):
            self.options[i].default = (i == selected-1)
        await interaction.response.edit_message(view=self.view)


class Grade(discord.ui.Select):
    view: DataCreateView

    def __init__(self):
        super().__init__(
            placeholder="学年を選択...",
            options=[
                discord.SelectOption(label="1年生", value="1"),
                discord.SelectOption(label="2年生", value="2"),
                discord.SelectOption(label="3年生", value="3")
            ]
        )

    async def callback(self, interaction):
        selected = int(self.values[0])
        for i in range(3):
            self.options[i].default = (i == selected-1)
        sub = Subject(selected-1)
        await sub.async_setup()
        self.view.add_item(sub)
        await interaction.response.edit_message(view=self.view)


class Subject(discord.ui.Select):
    def __init__(self, grade: int):
        super().__init__(placeholder="教科を選択...")
        self.grade = grade

    async def async_setup(self):
        sub = await self.view.bot.cogs["Examination"].execute_sql("SELECT * FROM subject;")
        for i in sub:
            if i[2] & self.grade:
                self.add_option(label=i[1], value=str(i[0]))

    async def callback(self, interaction):
        selected = int(self.values[0])
        for i in range(3):
            self.options[i].default = (int(self.options[i].value) == selected)
        await interactrion.response.edit_message(view=self.view)


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
        view = DataCreateView(self.bot)
        await ctx.send("学年とテストの種類を選択してください。", view=view)

    @commands.hybrid_command()
    async def view(self, ctx: commands.Context):
        await ctx.send("test2!")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Examination(bot))
