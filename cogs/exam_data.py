from discord.ext import commands
import discord
import aiomysql
import os


class DataCreateView(discord.ui.View):
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
        for i in range(4):
            self.options[i].default = (i == selected-1)
        await interaction.response.edit_message(view=self.view)


class SubmitButton(discord.ui.Button):
    def __init__(self, mode: int):
        super().__init__(label="次へ")
        self.mode = mode

    async def callback(self, interaction):
        if self.mode == 1:
            # self.view.add_item()
            grade = self.view.get_item(Grade)
            if not grade.values:
                return await interaction.response.send_message("先に学年を指定してください。", ephemeral=True)
            await interaction.response.edit_message(content="教科を選択してください。")
        else:
            ...


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
        view = DataCreateView()
        view.add_item(Grade())
        view.add_item(TestType())
        view.add_item(SubmitButton(1))
        await ctx.send("学年とテストの種類を選択してください。", view=view)

    @commands.hybrid_command()
    async def view(self, ctx: commands.Context):
        await ctx.send("test2!")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Examination(bot))
