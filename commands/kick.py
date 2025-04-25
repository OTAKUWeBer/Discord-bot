import discord
from discord.ext import commands
from discord import app_commands, Interaction

class Kick(commands.Cog):
    """Kick a member from the server with optional reason."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx: commands.Context, user: discord.Member, *, reason: str = None):
        if user == ctx.author:
            return await ctx.send("❌ You cannot kick yourself.")
        try:
            await user.kick(reason=reason)
            embed = discord.Embed(
                title="Member Kicked",
                color=discord.Color.red()
            )
            embed.add_field(name="User", value=user.mention, inline=True)
            embed.add_field(name="By", value=ctx.author.mention, inline=True)
            if reason:
                embed.add_field(name="Reason", value=reason, inline=False)
            await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to kick that user.")
        except Exception as e:
            await ctx.send(f"⚠️ An error occurred: {e}")

    @app_commands.command(name="kick", description="Kick a member from the server")
    @app_commands.checks.has_permissions(kick_members=True)
    async def slash_kick(self, interaction: Interaction, user: discord.Member, reason: str = None):
        """Slash command: /kick @user [reason]"""
        if user == interaction.user:
            return await interaction.response.send_message("❌ You cannot kick yourself.", ephemeral=True)
        try:
            await interaction.guild.kick(user, reason=reason)
            embed = discord.Embed(
                title="Member Kicked",
                color=discord.Color.red()
            )
            embed.add_field(name="User", value=user.mention, inline=True)
            embed.add_field(name="By", value=interaction.user.mention, inline=True)
            if reason:
                embed.add_field(name="Reason", value=reason, inline=False)
            await interaction.response.send_message(embed=embed)
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to kick that user.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"⚠️ An error occurred: {e}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Kick(bot))
