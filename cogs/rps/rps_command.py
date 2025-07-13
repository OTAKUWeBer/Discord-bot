import discord
from discord.ext import commands
from discord import app_commands, Interaction
import random
from typing import Literal

class RockPaperScissors(commands.Cog):
    """Simple Rock-Paper-Scissors game."""
    OPTIONS = ["rock", "paper", "scissors"]

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def _decide_winner(self, user_choice: str, bot_choice: str) -> str:
        # Returns "win", "lose" or "tie"
        if user_choice == bot_choice:
            return "tie"
        wins = {
            "rock": "scissors",
            "paper": "rock",
            "scissors": "paper",
        }
        return "win" if wins[user_choice] == bot_choice else "lose"

    @commands.command(name="rps", help="Play Rock-Paper-Scissors. Usage: !rps <rock|paper|scissors>")
    async def rps(self, ctx: commands.Context, choice: str):
        choice = choice.lower()
        if choice not in self.OPTIONS:
            return await ctx.send(f"Invalid choice! Please choose one of: {', '.join(self.OPTIONS)}.")

        bot_choice = random.choice(self.OPTIONS)
        result = self._decide_winner(choice, bot_choice)

        embed = discord.Embed(title="🕹️ Rock-Paper-Scissors", color=discord.Color.green())
        embed.add_field(name="Your choice", value=choice.capitalize(), inline=True)
        embed.add_field(name="My choice", value=bot_choice.capitalize(), inline=True)

        if result == "tie":
            desc = "It's a tie!"
            embed.color = discord.Color.gold()
        elif result == "win":
            desc = "You win! 🎉"
            embed.color = discord.Color.blue()
        else:
            desc = "You lose! 😢"
            embed.color = discord.Color.red()

        embed.description = desc
        await ctx.send(embed=embed)

    @app_commands.command(name="rps", description="Play Rock-Paper-Scissors against the bot.")
    async def rps_slash(self, interaction: Interaction, choice: Literal["rock", "paper", "scissors"]):
        """Slash command: /rps <choice>"""
        user_choice = choice.lower()
        bot_choice = random.choice(self.OPTIONS)
        result = self._decide_winner(user_choice, bot_choice)

        embed = discord.Embed(title="🕹️ Rock-Paper-Scissors", color=discord.Color.green())
        embed.add_field(name="Your choice", value=user_choice.capitalize(), inline=True)
        embed.add_field(name="My choice", value=bot_choice.capitalize(), inline=True)

        if result == "tie":
            desc = "It's a tie!"
            embed.color = discord.Color.gold()
        elif result == "win":
            desc = "You win! 🎉"
            embed.color = discord.Color.blue()
        else:
            desc = "You lose! 😢"
            embed.color = discord.Color.red()

        embed.description = desc
        await interaction.response.send_message(embed=embed)
async def setup(bot: commands.Bot):
    await bot.add_cog(RockPaperScissors(bot))
