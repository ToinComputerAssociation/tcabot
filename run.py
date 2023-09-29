import importlib

import discord
from discord.ext import commands
import dotenv
import os

dotenv.load_dotenv()

bot = commands.Bot(intents=discord.Intents.all(), command_prefix="tca!")

@bot.command()
@bot.is_owner()
async def restart(ctx):
    await ctx.send("Restart now...")
    await bot.close()
    main = importlib.reload_module("main")
    main.main(bot, token=os.getenv("TCABOT_TOKEN"))

main = importlib.import_module("main")
main.main(bot, token=os.getenv("TCABOT_TOKEN"))
