import discord
from discord.ext import commands
from discord import app_commands, Interaction

class RoleRemove(commands.Cog):
    """Remove role from members."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def _find_role(self, guild: discord.Guild, name: str) -> discord.Role | None:
        return discord.utils.get(guild.roles, name=name)

    @commands.command(name="removerole")
    @commands.has_permissions(manage_roles=True)
    async def removerole(self, ctx: commands.Context, user: discord.Member, *, role_name: str):
        role = self._find_role(ctx.guild, role_name)
        if not role:
            return await ctx.send(f"❌ Role `{role_name}` not found.")
        if role >= ctx.guild.me.top_role:
            return await ctx.send(f"❌ I can't remove `{role_name}`; it's higher than my highest role.")
        if role >= ctx.author.top_role:
            return await ctx.send(f"❌ You need a higher role to remove `{role_name}`.")
        await user.remove_roles(role)
        await ctx.send(f"✅ Removed `{role_name}` from {user.mention}.")

    @app_commands.command(name="removerole", description="Remove a role from a member")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def slash_removerole(self, interaction: Interaction, user: discord.Member, role_name: str):
        role = self._find_role(interaction.guild, role_name)
        if not role:
            return await interaction.response.send_message(f"❌ Role `{role_name}` not found.", ephemeral=True)
        if role >= interaction.guild.me.top_role:
            return await interaction.response.send_message(
                f"❌ I can't remove `{role_name}`; it's higher than my highest role.", ephemeral=True
            )
        if role >= interaction.user.top_role:
            return await interaction.response.send_message(
                f"❌ You need a higher role to remove `{role_name}`.", ephemeral=True
            )
        await user.remove_roles(role)
        await interaction.response.send_message(f"✅ Removed `{role_name}` from {user.mention}.")

async def setup(bot: commands.Bot):
    await bot.add_cog(RoleRemove(bot))
