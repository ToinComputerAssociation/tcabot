import traceback
import discord
from discord.ext import commands
import os
import dotenv

# cwdをこのファイルがある場所に移動
os.chdir(os.path.dirname(os.path.abspath(__file__)))


dotenv.load_dotenv()

bot = commands.Bot(intents=discord.Intents.all(), command_prefix="tca!")

@bot.event
async def on_ready():
    await bot.load_extension("jishaku")
    for name in os.listdir("./cogs"):
        if not name.startswith((".", "_")):
            try:
                await bot.load_extension("cogs."+name.replace(".py", ""))
            except Exception as e:
                print("".join(traceback.format_exception(e)))
    await bot.tree.sync()
    print("[log] Just ready for TCABot")

@bot.tree.error
async def on_error(interaction, error):
    await discord.app_commands.CommandTree.on_error(bot.tree, interaction, error)
    err = "".join(traceback.format_exception(error))
    embed = discord.Embed(description=f"```py\n{err}\n```"[:4095])
    if interaction.response.is_done():
        await interaction.channel.send("An error has occurred.", embed=embed)
    else:
        await interaction.response.send_message("An error has occurred.", embed=embed)


bot.run(token=os.getenv("TCABOT_TOKEN"))
