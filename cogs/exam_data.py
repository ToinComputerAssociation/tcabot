from typing import Optional, Literal
from discord.ext import commands
import discord
import aiomysql
import os


class DataCreateView(discord.ui.View):
    def __init__(self, bot):
        super().__init__()
        self.add_item(Grade())
        self.add_item(TestType())
        self.add_item(Year())
        self.add_item(SubmitButton())
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
        try:
            self.view.remove_item(self.view.get_item(Subject))
        except KeyError:
            pass
        sub = Subject(selected-1)
        self.view.add_item(sub)
        await sub.async_setup()
        await interaction.response.edit_message(view=self.view)


class Subject(discord.ui.Select):
    def __init__(self, grade: int):
        super().__init__(placeholder="教科を選択...")
        self.grade = grade

    async def async_setup(self):
        sub = await self.view.bot.cogs["Examination"].execute_sql("SELECT * FROM subject;")
        for i in sub:
            if i[2] & (1 << self.grade):
                self.add_option(label=i[1], value=str(i[0]))

    async def callback(self, interaction: discord.Interaction):
        selected = int(self.values[0])
        for i in range(len(self.options)):
            self.options[i].default = (int(self.options[i].value) == selected)
        await interaction.response.edit_message(view=self.view)


class Year(discord.ui.Select):
    def __init__(self):
        super().__init__(
            placeholder="年を選択...",
            options=[
                discord.SelectOption(label="2023年", value="2023"),
                discord.SelectOption(label="2022年", value="2022"),
                discord.SelectOption(label="2021年", value="2021"),
                discord.SelectOption(label="2020年", value="2020"),
                discord.SelectOption(label="2019年", value="2019"),
                discord.SelectOption(label="2018年", value="2018"),
                discord.SelectOption(label="2017年", value="2017"),
                discord.SelectOption(label="2016年", value="2016"),
                discord.SelectOption(label="2015年", value="2015")
            ]
        )

    async def callback(self, interaction: discord.Interaction):
        selected = int(self.values[0])
        for i in range(len(self.options)):
            self.options[i].default = (int(self.options[i].value) == selected)
        await interaction.response.edit_message(view=self.view)


class SubmitButton(discord.ui.Button):
    view: DataCreateView

    def __init__(self):
        super().__init__(label="決定")

    async def callback(self, interaction):
        grade = self.view.get_item(Grade).values
        if not grade:
            return await interaction.response.send_message("先に学年を指定してください。", ephemeral=True)
        year = self.view.get_item(Year).values
        testtype = self.view.get_item(TestType).values
        subject = self.view.get_item(Subject).values
        if not (year and testtype and subject):
            return await interaction.response.send_message("すべての項目を先に選択してください。", ephemeral=True)

        await self.view.bot.cogs["Examination"].execute_sql(
            "INSERT INTO main values (%s, %s, %s, NULL, %s, NULL);",
            (int(year[0]), int(grade[0]), int(subject[0]), int(testtype[0]))
        )
        await interaction.response.edit_message(content="登録しました。", view=None)


class Examination(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def cog_load(self):
        self.pool = await aiomysql.create_pool(
            host=os.environ["MYSQL_HOST"], port=int(os.environ["MYSQL_PORT"]),
            user=os.environ["MYSQL_USERNAME"], password=os.environ["MYSQL_PASSWORD"],
            db=os.environ["MYSQL_DBNAME"], loop=self.bot.loop, autocommit=True
        )
        # memo: データベース `main` の構造 -> (Year, Grade, Subject, Classes, Type, Teacher)

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
    async def search(
        self, ctx: commands.Context,
        year: Literal[2023, 2022, 2021, 2020, 2019, 2018, 2017, 2016, 2015],
        testtype: Literal["前期中間", "前期期末", "後期中間", "後期期末"],
        subject: Literal[
            "数学I", "数学II", "数学III", "数学A", "数学B", "数学C",
            "現代の国語", "言語文化", "歴史総合", "地理総合", "生物基礎", "生物",
            "科学基礎", "科学", "地学基礎", "地学", "物理基礎", "物理",
            "英語コミュニケーションI", "論理表現I", "英語コミュニケーションII", "論理表現II",
            "英語コミュニケーションIII", "論理表現III", "情報"
        ]
    ):
        await ctx.send("test2!")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Examination(bot))
