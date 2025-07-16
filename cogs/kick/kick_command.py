import discord
from discord.ext import commands
from discord import app_commands, Interaction
from datetime import datetime
import os
from .utils.logger import write_to_log_csv

from dotenv import load_dotenv

load_dotenv()

LOG_CHANNEL_ID = int(os.getenv("KICK_LOG_CHANNEL_ID"))

class Kick(commands.Cog):
    """Kick a member from the server with optional reason."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def log_kick(self, guild: discord.Guild, user: discord.Member, moderator: discord.abc.User, reason: str = None):
        timestamp = datetime.utcnow()
        reason = reason or "No reason provided."

        # Log to mod-log channel
        log_channel = guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(title="🚪 Kick Log", color=discord.Color.orange(), timestamp=timestamp)
            embed.add_field(name="User", value=f"{user} ({user.id})", inline=False)
            embed.add_field(name="Kicked by", value=f"{moderator} ({moderator.id})", inline=False)
            embed.add_field(name="Reason", value=reason, inline=False)
            await log_channel.send(embed=embed)

        # Log to CSV file
        write_to_log_csv("KICK", str(user), user.id, str(moderator), moderator.id, reason)

    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx: commands.Context, user: discord.Member, *, reason: str = None):
        if user == ctx.author:
            return await ctx.send("❌ You cannot kick yourself.")
        try:
            await user.kick(reason=reason)
            await ctx.send(f"✅ {user.mention} has been kicked.")
            await self.log_kick(ctx.guild, user, ctx.author, reason)
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to kick that user.")
        except Exception as e:
            await ctx.send(f"⚠️ An error occurred: {e}")

    @app_commands.command(name="kick", description="Kick a member from the server")
    @app_commands.checks.has_permissions(kick_members=True)
    async def slash_kick(self, interaction: Interaction, user: discord.Member, reason: str = None):
        if user == interaction.user:
            return await interaction.response.send_message("❌ You cannot kick yourself.", ephemeral=True)
        try:
            await interaction.guild.kick(user, reason=reason)
            await interaction.response.send_message(f"✅ {user.mention} has been kicked.")
            await self.log_kick(interaction.guild, user, interaction.user, reason)
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to kick that user.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"⚠️ An error occurred: {e}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Kick(bot))
