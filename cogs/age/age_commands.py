import discord
from discord.ext import commands
from datetime import datetime

class AgeCommands(commands.Cog):
    """Account age commands."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def monthsage(self, ctx: commands.Context, user: discord.Member):
        account_creation_date = user.created_at.replace(tzinfo=None)
        current_date = datetime.now()
        days = (current_date - account_creation_date).days
        months, extra_days = divmod(days, 30)
        if extra_days >= 15:
            months += 1
        embed = discord.Embed(
            title="Account Age",
            description=f"{user.mention}'s account is {months} months old.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def daysage(self, ctx: commands.Context, user: discord.Member):
        days = (datetime.now() - user.created_at.replace(tzinfo=None)).days
        embed = discord.Embed(
            title="Account Age",
            description=f"{user.mention}'s account is {days} days old.",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def minutesage(self, ctx: commands.Context, user: discord.Member):
        mins = (datetime.now() - user.created_at.replace(tzinfo=None)).total_seconds() / 60
        embed = discord.Embed(
            title="Account Age",
            description=f"{user.mention}'s account is {int(mins)} minutes old.",
            color=discord.Color.gold()
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def secondsage(self, ctx: commands.Context, user: discord.Member):
        secs = (datetime.now() - user.created_at.replace(tzinfo=None)).total_seconds()
        embed = discord.Embed(
            title="Account Age",
            description=f"{user.mention}'s account is {int(secs)} seconds old.",
            color=discord.Color.teal()
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def microage(self, ctx: commands.Context, user: discord.Member):
        micro = int((datetime.now() - user.created_at.replace(tzinfo=None)).total_seconds() * 1_000_000)
        embed = discord.Embed(
            title="Account Age",
            description=f"{user.mention}'s account is {micro} microseconds old.",
            color=discord.Color.purple()
        )
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(AgeCommands(bot))
