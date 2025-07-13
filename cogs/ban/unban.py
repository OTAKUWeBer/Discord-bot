import discord
from discord.ext import commands
from discord import app_commands, Interaction

class Unban(commands.Cog):
    """Unban members (prefix and slash)."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Prefix command
    @commands.command(name="unban")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx: commands.Context, user_id: int):
        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(user)
            await ctx.send(f"✅ {user.mention} has been unbanned.")
        except discord.NotFound:
            await ctx.send("❌ User not found or not banned.")
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to unban users.")

    # Slash command
    @app_commands.command(name="unban", description="Unban a member from the server by ID")
    @app_commands.checks.has_permissions(ban_members=True)
    async def unban_slash(self, interaction: Interaction, user_id: int):
        try:
            user = await self.bot.fetch_user(user_id)
            await interaction.guild.unban(user)
            await interaction.response.send_message(
                f"✅ {user.mention} has been unbanned."
            )
        except discord.NotFound:
            await interaction.response.send_message(
                "❌ User not found or not banned.", ephemeral=True
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ I don't have permission to unban users.", ephemeral=True
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(Unban(bot))
