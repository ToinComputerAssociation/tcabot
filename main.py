def main(bot, token):
    @bot.event
    async def on_ready():
        await bot.load_extension("jishaku")

    bot.run(token=token)
