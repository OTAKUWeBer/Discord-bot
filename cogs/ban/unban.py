import discord
from discord.ext import commands
from discord import app_commands, Interaction
from datetime import datetime
import os
from .utils.logger import write_to_log_csv
from dotenv import load_dotenv

load_dotenv()

LOG_CHANNEL_ID = int(os.getenv("BAN_LOG_CHANNEL_ID"))

class Unban(commands.Cog):
    """Unban members (prefix and slash)."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def log_unban(self, guild: discord.Guild, target: discord.User, moderator: discord.abc.User):
        log_channel = guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(title="🟢 Unban Log", color=discord.Color.green(), timestamp=datetime.utcnow())
            embed.add_field(name="User", value=f"{target} ({target.id})", inline=False)
            embed.add_field(name="Unbanned by", value=f"{moderator} ({moderator.id})", inline=False)
            await log_channel.send(embed=embed)

        write_to_log_csv("UNBAN", str(target), target.id, str(moderator), moderator.id)

    @commands.command(name="unban")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx: commands.Context, user_id: int):
        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(user)
            await ctx.send(f"✅ {user.mention} has been unbanned.")
            await self.log_unban(ctx.guild, user, ctx.author)
        except discord.NotFound:
            await ctx.send("❌ User not found or not banned.")
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to unban users.")

    @app_commands.command(name="unban", description="Unban a member from the server by ID")
    @app_commands.checks.has_permissions(ban_members=True)
    async def unban_slash(self, interaction: Interaction, user_id: int):
        try:
            user = await self.bot.fetch_user(user_id)
            await interaction.guild.unban(user)
            await interaction.response.send_message(f"✅ {user.mention} has been unbanned.")
            await self.log_unban(interaction.guild, user, interaction.user)
        except discord.NotFound:
            await interaction.response.send_message("❌ User not found or not banned.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to unban users.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Unban(bot))
