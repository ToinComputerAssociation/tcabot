import discord
from discord.ext import commands
import dotenv
import os

dotenv.load_dotenv()

bot = commands.Bot(intents=discord.Intents.all(), command_prefix="tca!")

@bot.event
async def on_ready():
    await bot.load_extension("jishaku")

bot.run(token=os.getenv("TCABOT_TOKEN"))