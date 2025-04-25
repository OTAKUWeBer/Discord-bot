import discord
from discord.ext import commands
from discord import app_commands, Interaction

class Update(commands.Cog):
    """Show the latest features added to the bot."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

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
            value=(
                "- **Disconnect from Voice Channel**: Disconnect users from voice channels.\n"
                "- **Role Management**: Add or remove roles using the new commands.\n"
                "- **Slash Commands**: Use the `/` (slash) commands for enhanced functionality.\n"
                "- **Slap Command**: Send a slap GIF to a user.\n"
                "- **Gay Percentage**: Randomly rate how much gay someone is.\n"
                "- **Ping**: Check the bot's latency.\n"
                "- **Magic 8-Ball**: Ask any question and get a random answer."
            ),
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
            value=(
                "- **Disconnect from Voice Channel**: Disconnect users from voice channels.\n"
                "- **Role Management**: Add or remove roles using the new commands.\n"
                "- **Slash Commands**: Use the `/` (slash) commands for enhanced functionality.\n"
                "- **Slap Command**: Send a slap GIF to a user.\n"
                "- **Gay Percentage**: Randomly rate how much gay someone is.\n"
                "- **Ping**: Check the bot's latency.\n"
                "- **Magic 8-Ball**: Ask any question and get a random answer."
            ),
            inline=False
        )
        embed.set_footer(text="Type `/help` to view commands.")
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Update(bot))
