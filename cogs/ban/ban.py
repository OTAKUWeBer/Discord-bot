import discord
from discord.ext import commands
from discord import app_commands, Interaction

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

    # Prefix command
    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, member: discord.Member, *, reason: str = None):
        if not self.can_execute_action(ctx.author, member):
            return await ctx.send("❌ You cannot ban that user.")
        try:
            await member.ban(reason=reason)
            embed = discord.Embed(title="User Banned", color=discord.Color.dark_red())
            embed.add_field(name="User", value=member.mention, inline=True)
            embed.add_field(name="By", value=ctx.author.mention, inline=True)
            if reason:
                embed.add_field(name="Reason", value=reason, inline=False)
            await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to ban that user.")

    # Slash command
    @app_commands.command(name="ban", description="Ban a member from the server")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban_slash(self, interaction: Interaction, member: discord.Member, reason: str = None):
        if not self.can_execute_action(interaction.user, member):
            return await interaction.response.send_message(
                "❌ You cannot ban that user.", ephemeral=True
            )
        try:
            await interaction.guild.ban(member, reason=reason)
            embed = discord.Embed(title="User Banned", color=discord.Color.dark_red())
            embed.add_field(name="User", value=member.mention, inline=True)
            embed.add_field(name="By", value=interaction.user.mention, inline=True)
            if reason:
                embed.add_field(name="Reason", value=reason, inline=False)
            await interaction.response.send_message(embed=embed)
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ I don't have permission to ban that user.", ephemeral=True
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(Ban(bot))
