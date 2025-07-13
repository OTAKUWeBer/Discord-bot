import discord
from discord.ext import commands

class AgeHelp(commands.Cog):
    """Account age help commands."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="helpage")
    async def helpage(self, ctx: commands.Context):
        prefix = ctx.prefix
        embed = discord.Embed(
            title="Account Age Help",
            description="You can check your account age:",
            color=discord.Color.blue()
        )
        embed.add_field(name="In Months", value=f"```{prefix}monthsage @username```", inline=False)
        embed.add_field(name="In Days", value=f"```{prefix}daysage @username```", inline=False)
        embed.add_field(name="In Minutes", value=f"```{prefix}minutesage @username```", inline=False)
        embed.add_field(name="In Seconds", value=f"```{prefix}secondsage @username```", inline=False)
        embed.add_field(name="In Microseconds", value=f"```{prefix}microage @username```", inline=False)
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(AgeHelp(bot))
