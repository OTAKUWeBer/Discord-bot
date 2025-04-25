import discord
from discord.ext import commands
from discord import app_commands, Interaction

class HelpCog(commands.Cog):
    """List available commands and check bot latency."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="help")
    async def help(self, ctx: commands.Context):
        prefix = ctx.prefix

        embed = discord.Embed(
            title="Available Commands",
            description="Here are the commands:",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="Ask the Magic 8-Ball",
            value=f"```{prefix}8ball <question>```",
            inline=False
        )
        embed.add_field(
            name="Check Account Age",
            value=f"```{prefix}helpage```",
            inline=False
        )
        embed.add_field(
            name="Check How Much Gay (Random)",
            value=f"```{prefix}howmuchgay @username```",
            inline=False
        )
        embed.add_field(
            name="Kick or Ban User",
            value=f"```{prefix}kick , ban , unban @username```",
            inline=False
        )
        embed.add_field(
            name="Slap a Person",
            value=f"```{prefix}slap @username```",
            inline=False
        )
        embed.add_field(
            name="Disconnect a User",
            value=f"```{prefix}disconnect @username```",
            inline=False
        )
        embed.add_field(
            name="Give or Remove Role",
            value=f"```{prefix}giverole / {prefix}removerole @username```",
            inline=False
        )
        embed.add_field(
            name="Check What’s New",
            value=f"```{prefix}updates```",
            inline=False
        )
        await ctx.send(embed=embed)

    @app_commands.command(name="help", description="Show available commands")
    async def help_slash(self, interaction: Interaction):
        """Slash command: /help - List available commands"""
        embed = discord.Embed(
            title="Available Commands",
            description="Here are the commands:",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="Ask the Magic 8-Ball",
            value="```/8ball <question>```",
            inline=False
        )
        embed.add_field(
            name="Check Account Age",
            value="```/helpage```",
            inline=False
        )
        embed.add_field(
            name="Check How Much Gay (Random)",
            value="```/howmuchgay @username```",
            inline=False
        )
        embed.add_field(
            name="Kick or Ban User",
            value="```/kick , ban , unban @username```",
            inline=False
        )
        embed.add_field(
            name="Slap a Person",
            value="```/slap @username```",
            inline=False
        )
        embed.add_field(
            name="Disconnect a User",
            value="```/disconnect @username```",
            inline=False
        )
        embed.add_field(
            name="Give or Remove Role",
            value="```/giverole / /removerole @username```",
            inline=False
        )
        embed.add_field(
            name="Check What’s New",
            value="```/updates```",
            inline=False
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCog(bot))
