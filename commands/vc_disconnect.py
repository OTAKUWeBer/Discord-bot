import discord
from discord.ext import commands
from discord import app_commands, Interaction

class Disconnect(commands.Cog):
    """Disconnect a member from a voice channel."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="disconnect")
    @commands.has_permissions(move_members=True)
    async def disconnect(self, ctx: commands.Context, member: discord.Member):
        if member.voice and member.voice.channel:
            try:
                await member.move_to(None)
                await ctx.send(f"✅ {member.mention} has been disconnected from the voice channel.")
            except discord.Forbidden:
                await ctx.send("❌ I don't have permission to move that user.")
        else:
            await ctx.send(f"❌ {member.mention} is not connected to a voice channel.")

    @app_commands.command(name="disconnect", description="Disconnect a member from a voice channel")
    @app_commands.checks.has_permissions(move_members=True)
    async def slash_disconnect(self, interaction: Interaction, member: discord.Member):
        """Slash command: /disconnect @user"""
        await interaction.response.defer(ephemeral=True)
        if member.voice and member.voice.channel:
            try:
                await member.move_to(None)
                await interaction.followup.send(
                    f"✅ {member.mention} has been disconnected from the voice channel.",
                )
            except discord.Forbidden:
                await interaction.followup.send(
                    "❌ I don't have permission to move that user.", ephemeral=True
                )
        else:
            await interaction.followup.send(
                f"❌ {member.mention} is not connected to a voice channel.", ephemeral=True
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(Disconnect(bot))
