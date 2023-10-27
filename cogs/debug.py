from discord.ext import commands

class Debug(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(aliases=["sql"])
    async def execute_tsuq_sql(self, ctx, arg):
        r = await self.bot.cogs["Examination"].execute_sql(arg)
        await ctx.send(f"Command was executed successfully.\n```\n{r or '(Nothing Returned)'}\n```")

async def setup(bot):
    await bot.add_cog(Debug(bot))
