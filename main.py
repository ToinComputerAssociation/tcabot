import traceback
import discord
from discord.ext import commands
import os
import dotenv

# cwdをこのファイルがある場所に移動
os.chdir(os.path.dirname(os.path.abspath(__file__)))
# .envファイルの読み込み
dotenv.load_dotenv()
token = os.getenv("TCABOT_TOKEN")
if not token:
    print("エラー: .envファイルにTCABOT_TOKENを設定してください。")
    input("Press Enter to exit...")
    exit(1)


bot = commands.Bot(intents=discord.Intents.all(), command_prefix="tca!")


@bot.event
async def on_ready():
    bot.owner_ids = [693025129806037003, 850297484965576754]

    # cogの読み込み
    await bot.load_extension("jishaku")
    for name in os.listdir("./cogs"):
        if not (name.startswith((".", "_")) or name == "money.py"):
            try:
                await bot.load_extension("cogs."+name.replace(".py", ""))
            except Exception as e:
                print("".join(traceback.format_exception(e)))

    # moneyのみ最後に読み込む
    try:
        await bot.load_extension("cogs.money")
    except Exception as e:
        print("".join(traceback.format_exception(e)))

    await bot.tree.sync()
    print("[log] Just ready for TCABot")


@bot.tree.error
async def on_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    await discord.app_commands.CommandTree.on_error(bot.tree, interaction, error)
    err = "".join(traceback.format_exception(error))
    embed = discord.Embed(description=f"```py\n{err}\n```"[:4095])
    if interaction.response.is_done():
        if isinstance(interaction.channel, discord.TextChannel):
            await interaction.channel.send("An error has occurred.", embed=embed)
    else:
        await interaction.response.send_message("An error has occurred.", embed=embed)


bot.run(token=token)
