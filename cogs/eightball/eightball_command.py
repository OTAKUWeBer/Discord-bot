import discord
from discord.ext import commands
from discord import app_commands, Interaction
import random

class EightBall(commands.Cog):
    """Magic 8-Ball: Ask a question and get a random answer."""
    RESPONSES = [
        "It is certain.", "It is decidedly so.", "Without a doubt.",
        "Yes – definitely.", "You may rely on it.", "As I see it, yes.",
        "Most likely.", "Outlook good.", "Yes.", "Signs point to yes.",
        "Reply hazy, try again.", "Ask again later.", "Better not tell you now.",
        "Cannot predict now.", "Concentrate and ask again.",
        "Don't count on it.", "My reply is no.", "My sources say no.",
        "Outlook not so good.", "Very doubtful."
    ]

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="8ball")
    async def eightball(self, ctx: commands.Context, *, question: str):
        answer = random.choice(self.RESPONSES)
        embed = discord.Embed(title="🎱 Magic 8-Ball", color=discord.Color.purple())
        embed.add_field(name="Question", value=question, inline=False)
        embed.add_field(name="Answer", value=answer, inline=False)
        await ctx.send(embed=embed)

    @app_commands.command(name="8ball", description="Ask the magic 8-ball a question")
    async def eightball_slash(self, interaction: Interaction, question: str):
        """Slash command: /8ball <question>"""
        answer = random.choice(self.RESPONSES)
        embed = discord.Embed(title="🎱 Magic 8-Ball", color=discord.Color.purple())
        embed.add_field(name="Question", value=question, inline=False)
        embed.add_field(name="Answer", value=answer, inline=False)
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(EightBall(bot))
