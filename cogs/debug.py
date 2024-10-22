import discord
from discord.ext import commands
from traceback import format_exception as fmt_exc
from jishaku.codeblocks import Codeblock


class Debug(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

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

    @commands.command()
    @commands.is_owner()
    async def pullre(self, ctx: commands.Context, cog_name: str | None = None):
        git = await self.bot.get_command("jishaku git")
        await ctx.invoke(git, "pull")
        if cog_name is None:
            cog_name = "cogs.*"
        reload = await self.bot.get_command("jishaku reload")
        await ctx.invoke(reload, cog_name)


async def setup(bot):
    await bot.add_cog(Debug(bot))
