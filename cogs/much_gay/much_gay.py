import discord
from discord.ext import commands
from discord import app_commands, Interaction
from random import randint

class HowMuchGay(commands.Cog):
    """Calculate and display a random "gay percentage" for a user."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="howmuchgay")
    async def howmuchgay(self, ctx: commands.Context, user: discord.Member):
        pct = randint(1, 100)
        embed = discord.Embed(
            title="Gay Percentage",
            description=f"{user.mention} is {pct}% gay",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)

    @app_commands.command(name="howmuchgay", description="Check how much gay a user is")
    async def howmuchgay_slash(self, interaction: Interaction, user: discord.Member):
        """Slash command: /howmuchgay @user"""
        pct = randint(1, 100)
        embed = discord.Embed(
            title="Gay Percentage",
            description=f"{user.mention} is {pct}% gay",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(HowMuchGay(bot))