import discord
from discord.ext import commands
from discord import app_commands, Interaction
from .music_state import MusicState

class Resume(commands.Cog):
    def __init__(self, bot, music_state):
        self.bot = bot
        self.music = music_state
        
    @commands.command(name="resume", help="Resume a paused song")
    async def resume(self, ctx: commands.Context):
        vc = self.music.voice_client
        if not vc:
            return await ctx.send("Not connected to any voice channel.")
        if not vc.is_paused():
            return await ctx.send("▶️ Nothing is paused currently.")

        self.music.resume()
        vc.resume()
        embed = discord.Embed(
            description="▶️ Music resumed",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)

    @app_commands.command(name="resume", description="Resume a paused song")
    async def resume_slash(self, interaction: Interaction):
        vc = self.music.voice_client
        if not vc:
            return await interaction.response.send_message("Not connected to any voice channel.", ephemeral=True)
        if not vc.is_paused():
            return await interaction.response.send_message("▶️ Nothing is paused currently.", ephemeral=True)

        self.music.resume()
        vc.resume()
        embed = discord.Embed(
            description="▶️ Music resumed",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Resume(bot))