import traceback
import os

def main(bot, token):
    @bot.event
    async def on_ready():
        await bot.load_extension("jishaku")
        for name in os.listdir("cogs"):
            if not name.startswith("."):
                try:
                    await bot.load_extension("cogs."+name.replace(".py", ""))
                except Exception as e:
                    print("".join(traceback.format_exception(e)))
    bot.run(token=token)
