from discord.ext import commands
from discord import app_commands
import discord
import json
import datetime


class PaymentSelectButton(discord.ui.Button):
    def __init__(self, name: str, callback):
        super().__init__(style=discord.ButtonStyle.green, label=name)
        self.original_callback = callback
    
    async def callback(self, interaction):
        await self.original_callback(interaction, self)


class Money(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.execute_sql = bot.cogs["Examination"].execute_sql
        super().__init__()

    async def cog_load(self):
        await self.execute_sql(
            """CREATE TABLE IF NOT EXISTS money (
                user_id BIGINT NOT NULL, payment_type TEXT(255), value BIGINT,
                PRIMARY KEY(user_id, payment_type(255))
            );"""
        )
        await self.execute_sql(
            """CREATE TABLE IF NOT EXISTS money_settings (
                user_id BIGINT PRIMARY KEY NOT NULL, is_ephemeral BOOLEAN, logger BOOLEAN,
                payment_types JSON
            );"""
        )
        await self.execute_sql(
            """CREATE TABLE IF NOT EXISTS money_log (
                user_id BIGINT NOT NULL, time TIMESTAMP, payment_type TEXT(255), amount BIGINT, reason TEXT,
                PRIMARY KEY(user_id, time)
            );"""
        )

    async def load_settings(self, user_id: int):
        data = await self.execute_sql(
            "SELECT * FROM money_settings WHERE user_id = %s;", (user_id,)
        )
        if not data:
            await self.execute_sql(
                "INSERT INTO money_settings VALUES (%s, TRUE, TRUE, '[]');", (user_id,)
            )
            return {"is_ephemeral": True, "logger": True, "payment_types": []}
        return {"is_ephemeral": bool(data[0][1]), "logger": bool(data[0][2]), "payment_types": json.loads(data[0][3])}

    async def pay_or_charge(self, user_id: int, payment_type: str, amount: int, reason: str | None, is_logger: bool):
        if is_logger:
            current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            await self.execute_sql(
                "INSERT INTO money_log VALUES (%s, %s, %s, %s, %s)",
                (user_id, current_date, payment_type, amount, reason)
            )
        await self.execute_sql(
            "INSERT INTO money VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE value = value + %s;",
            (user_id, payment_type, amount, amount)
        )

    async def get_money(self, user_id, payment_type):
        data = await self.execute_sql(
            "SELECT * FROM money WHERE user_id = %s AND payment_type = %s;", (user_id, payment_type)
        )
        return data[0][2]

    @commands.hybrid_group(fallback="status", description="所持金の情報を確認します。")
    @app_commands.allowed_installs(guilds=True, users=True)
    async def money(self, ctx: commands.Context):
        if ctx.invoked_subcommand:
            return
        settings = await self.load_settings(ctx.author.id)
        status = []
        for i in settings["payment_types"]:
            data = await self.execute_sql(
                "SELECT * FROM money WHERE user_id = %s AND payment_type = %s;", (ctx.author.id, i)
            )
            if data:
                status.append(f"- {i}: **{data[0][2]}**円")
        await ctx.send(f"あなたの所持金情報\n{'\n'.join(status)}", ephemeral=settings["is_ephemeral"])

    @money.group(fallback="view", description="moneyシステムの設定を確認します。")
    async def settings(self, ctx: commands.Context):
        if ctx.invoked_subcommand:
            return
        settings = await self.load_settings(ctx.author.id)
        def yesno(condition):
            return "はい" if condition else "いいえ"
        await ctx.send(
            f"**あなたの設定状況**\n- 登録済みの支払い方法：{len(settings["payment_types"])}種\n"
            f"- 他人から見えないメッセージにするか：{yesno(settings["is_ephemeral"])}\n- ログを保存するか：{yesno(settings["logger"])}",
            ephemeral=settings["is_ephemeral"]
        )

    @settings.command(description="支払い方法を追加します。")
    @app_commands.describe(name="追加する支払い方法の名称")
    async def add_payment(self, ctx: commands.Context, name: str):
        settings = await self.load_settings(ctx.author.id)
        if name in settings["payment_types"]:
            return await ctx.send(f"エラー：{name}はすでに支払い方法に入っています。", ephemeral=settings["is_ephemeral"])
        settings["payment_types"].append(name)
        await self.execute_sql(
            "UPDATE money_settings SET payment_types = %s WHERE user_id = %s;", (json.dumps(settings["payment_types"]), ctx.author.id)
        )
        await ctx.send(f"支払い方法に{name}を追加しました。", ephemeral=settings["is_ephemeral"])

    @settings.command(description="支払い方法を削除します。")
    @app_commands.describe(name="削除する支払い方法の名称")
    async def remove_payment(self, ctx: commands.Context, name: str):
        settings = await self.load_settings(ctx.author.id)
        if name not in settings["payment_types"]:
            return await ctx.send(f"エラー：{name}は支払い方法に入っていません。", ephemeral=settings["is_ephemeral"])
        settings["payment_types"].remove(name)
        await self.execute_sql(
            "UPDATE money_settings SET payment_types = %s WHERE user_id = %s;", (json.dumps(settings["payment_types"]), ctx.author.id)
        )
        await ctx.send(f"支払い方法から{name}を削除しました。", ephemeral=settings["is_ephemeral"])

    @settings.command(description="メッセージを他人に見える状態にするかどうかを変更します。")
    async def hide(self, ctx: commands.Context):
        settings = await self.load_settings(ctx.author.id)
        mode = not settings["is_ephemeral"]
        await self.execute_sql(
            "UPDATE money_settings SET is_ephemeral = %s WHERE user_id = %s;", (mode, ctx.author.id)
        )
        await ctx.send(f"メッセージが他人から見え{"ない" if mode else "る"}ようになりました。", ephemeral=mode)

    @money.command(description="支払いを記録します。")
    @app_commands.describe(amount="支払った金額", reason="支払い理由 (省略可)")
    async def pay(self, ctx: commands.Context, amount: int, reason: str | None = None):
        settings = await self.load_settings(ctx.author.id)
        if not settings["payment_types"]:
            return await ctx.send(
                "エラー：支払い方法が登録されていません。`/money settings add_payment [名前]`で登録してください。",
                ephemeral=settings["is_ephemeral"]
            )

        async def button_callback(interaction: discord.Interaction, button: discord.ui.Button):
            await self.pay_or_charge(ctx.author.id, button.label, -amount, reason, settings["logger"])
            left = await self.get_money(ctx.author.id, button.label)
            await interaction.response.edit_message(
                content=f"支払いを記録しました。\n> `{button.label}`で`{amount}`円支払い\n> 残額：`{left}`円",
                view=None
            )

        view = discord.ui.View()
        for name in settings["payment_types"]:
            view.add_item(PaymentSelectButton(name, button_callback))

        await ctx.send("どの方法で支払いましたか？(選択)", view=view, ephemeral=settings["is_ephemeral"])

    @money.command(description="チャージを記録します。")
    @app_commands.describe(amount="チャージした金額", reason="チャージ理由 (省略可)")
    async def charge(self, ctx: commands.Context, amount: int, reason: str | None = None):
        settings = await self.load_settings(ctx.author.id)
        if not settings["payment_types"]:
            return await ctx.send(
                "支払い方法が登録されていません。`/money settings add_payment [名前]`で登録してください。",
                ephemeral=settings["is_ephemeral"]
            )

        async def button_callback(interaction: discord.Interaction, button: discord.ui.Button):
            await self.pay_or_charge(ctx.author.id, button.label, amount, reason, settings["logger"])
            left = await self.get_money(ctx.author.id, button.label)
            await interaction.response.edit_message(
                content=f"チャージを記録しました。\n> `{button.label}`に`{amount}`円\n> 残額：`{left}`円",
                view=None
            )

        view = discord.ui.View()
        for name in settings["payment_types"]:
            view.add_item(PaymentSelectButton(name, button_callback))

        await ctx.send(f"どれにチャージしましたか？(選択)", view=view, ephemeral=settings["is_ephemeral"])

    @money.command(description="金額を別の支払い方法へ移動させます。")
    @app_commands.describe(amount="移動した金額", reason="移動理由(省略可)")
    async def move(self, ctx: commands.Context, amount: int, reason: str | None = None):
        settings = await self.load_settings(ctx.author.id)
        if not settings["payment_types"]:
            return await ctx.send(
                "支払い方法が登録されていません。`/money settings add_payment [名前]`で登録してください。",
                ephemeral=settings["is_ephemeral"]
            )
        if len(settings["payment_types"]) < 2:
            return await ctx.send(
                "支払い方法が2つ以上ないとこのコマンドは使用できません。`/money settings add_payment [名前]`で登録してください。",
                ephemeral=settings["is_ephemeral"]
            )

        data = []

        async def button_callback_2(interaction: discord.Interaction, button: discord.ui.Button):
            data.append(button.label)
            await self.pay_or_charge(ctx.author.id, data[0], -amount, (reason or "") + "(移動)", settings["logger"])
            await self.pay_or_charge(ctx.author.id, data[1], amount, (reason or "") + "(移動)", settings["logger"])
            left = await self.execute_sql(
                "SELECT * FROM money WHERE user_id = %s AND payment_type IN %s;", (ctx.author.id, data)
            )
            await interaction.response.edit_message(
                content=f"移動を記録しました。\n> `{data[0]}`から`{data[1]}`へ`{amount}`円\n"
                        f"{data[0]}残額：{left[0]}円、{data[1]}残額：{left[1]}円",
                view=None
            )

        view = discord.ui.View()

        async def button_callback(interaction: discord.Interaction, button: discord.ui.Button):
            data.append(button.label)
            view = discord.ui.View()
            for name in settings["payment_types"]:
                btn = PaymentSelectButton(name, button_callback_2)
                if name == button.label:
                    btn.disabled = True
                view.add_item(btn)
            await interaction.response.edit_message(
                content="どの支払い方法へ移動させましたか？(選択)", view=view
            )

        for name in settings["payment_types"]:
            view.add_item(PaymentSelectButton(name, button_callback))

        await ctx.send("どの支払い方法から移動しましたか？(選択)", view=view, ephemeral=settings["is_ephemeral"])

    @money.command(description="支払い履歴を表示します。")
    @app_commands.describe(
        payment_type="支払い方法での絞り込み (指定なしで全種類)",
        # TODO: afterやbefore、reasonでの検索もできるように
    )
    async def log(self, ctx: commands.Context, payment_type: str | None = None):
        settings = await self.load_settings(ctx.author.id)
        if payment_type:
            data = await self.execute_sql(
                "SELECT * FROM money_log WHERE user_id = %s AND payment_type = %s ORDER BY time DESC LIMIT 20;",
                (ctx.author.id, payment_type)
            )
        else:
            data = await self.execute_sql(
                "SELECT * FROM money_log WHERE user_id = %s ORDER BY time DESC LIMIT 20;", (ctx.author.id,)
            )
        logs = []
        for item in data:
            logs.append(
                f"{"+" if item[3] > 0 else "-"} {item[1].strftime("%m月%d日%H時%M分")} {item[2]}"
                f"{"にチャージ" if item[3] > 0 else "で支払い　"} {abs(item[3]):>5}円 {item[4] or "(理由なし)"}"
            )
        await ctx.send(f"直近の取引ログ(最大20件)\n```diff\n{"\n".join(logs) or "該当ログなし"}\n```", ephemeral=settings["is_ephemeral"])


async def setup(bot: commands.Bot):
    await bot.add_cog(Money(bot))
