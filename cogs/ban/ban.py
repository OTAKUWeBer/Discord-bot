import discord
from discord.ext import commands
from discord import app_commands, Interaction
from datetime import datetime
import os
from .utils.logger import write_to_log_csv

from dotenv import load_dotenv

load_dotenv()

LOG_CHANNEL_ID = int(os.getenv("BAN_LOG_CHANNEL_ID"))

class Ban(commands.Cog):
    """Ban members (prefix and slash)."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def can_execute_action(self, issuer: discord.Member, target: discord.Member) -> bool:
        return (
            issuer.guild_permissions.ban_members and
            issuer != target and
            issuer.top_role > target.top_role
        )

    async def log_ban(self, guild: discord.Guild, target: discord.Member, moderator: discord.Member, reason: str):
        # Log to Discord channel
        log_channel = guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(title="🔨 Ban Log", color=discord.Color.red(), timestamp=datetime.utcnow())
            embed.add_field(name="User", value=f"{target} ({target.id})", inline=False)
            embed.add_field(name="Banned by", value=f"{moderator} ({moderator.id})", inline=False)
            embed.add_field(name="Reason", value=reason or "No reason provided.", inline=False)
            await log_channel.send(embed=embed)

        # Log to CSV
        write_to_log_csv("BAN", str(target), target.id, str(moderator), moderator.id, reason or "")

    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, member: discord.Member, *, reason: str = None):
        if not self.can_execute_action(ctx.author, member):
            return await ctx.send("❌ You cannot ban that user.")
        try:
            await member.ban(reason=reason)
            await ctx.send(f"✅ {member.mention} has been banned.")
            await self.log_ban(ctx.guild, member, ctx.author, reason)
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to ban that user.")

    @app_commands.command(name="ban", description="Ban a member from the server")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban_slash(self, interaction: Interaction, member: discord.Member, reason: str = None):
        if not self.can_execute_action(interaction.user, member):
            return await interaction.response.send_message("❌ You cannot ban that user.", ephemeral=True)
        try:
            await interaction.guild.ban(member, reason=reason)
            await interaction.response.send_message(f"✅ {member.mention} has been banned.")
            await self.log_ban(interaction.guild, member, interaction.user, reason)
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to ban that user.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Ban(bot))
