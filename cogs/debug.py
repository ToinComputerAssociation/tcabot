import discord
from discord.ext import commands
from traceback import format_exception as fmt_exc


class Debug(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(aliases=["sql"])
    async def execute_tsuq_sql(self, ctx, *, arg):
        try:
            r = await self.bot.cogs["Examination"].execute_sql(arg)
        except Exception as exc:
            await ctx.send(
                "An error has occurred in command execution.",
                embed=discord.Embed(description=f"```py\n{''.join(fmt_exc(exc))}\n```")
            )
        else:
            await ctx.send(f"Command was executed successfully.\n```\n{r or '(Nothing Returned)'}\n```")


async def setup(bot):
    await bot.add_cog(Debug(bot))
