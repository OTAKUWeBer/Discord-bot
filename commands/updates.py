import discord
from discord.ext import commands
from discord import app_commands, Interaction

class Update(commands.Cog):
    """Show the latest features added to the bot."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Define this as a class-level or instance-level constant
    FEATURE_TEXT = (
        "- **Magic 8-Ball**: Ask any question and get a random answer.\n"
        "- **Rock-Paper-Scissors**: Play a game of Rock-Paper-Scissors against the bot.\n"
        "- **Play Song**: Play music from YouTube or search by song name using a command or slash.\n"
    )

    @commands.command(name="updates")
    async def updates(self, ctx: commands.Context):
        prefix = ctx.prefix
        embed = discord.Embed(
            title="Bot Updates",
            description="Here are the latest features added to the bot:",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="New Features",
            value=self.FEATURE_TEXT,
            inline=False
        )
        embed.set_footer(text=f"Type `{prefix}help` or `/help` to view commands.")
        await ctx.send(embed=embed)

    @app_commands.command(name="updates", description="See what new features have been added to the bot")
    async def updates_slash(self, interaction: Interaction):
        """Slash command: /updates - Show latest features"""
        embed = discord.Embed(
            title="Bot Updates",
            description="Here are the latest features added to the bot:",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="New Features",
            value=self.FEATURE_TEXT,
            inline=False
        )
        embed.set_footer(text="Type `/help` to view commands.")
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Update(bot))
