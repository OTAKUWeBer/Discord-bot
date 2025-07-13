import discord
from discord.ext import commands
from .music_state import MusicState
from discord import app_commands, Interaction


class Pause(commands.Cog):
    def __init__(self, bot, music_state):
        self.bot = bot
        self.music = music_state 
        
    @commands.command(name="pause", help="Pause the currently playing song")
    async def pause(self, ctx: commands.Context):
        vc = self.music.voice_client
        print("Pause command called")
        if not vc:
            print("No voice client")
            return await ctx.send("Not connected to a voice channel.")

        print("is_playing:", vc.is_playing(), "is_paused:", vc.is_paused())

        if vc.is_paused():
            return await ctx.send("⏸️ Already paused.")
        if not vc.is_playing():
            return await ctx.send("Nothing is playing right now.")

        self.music.pause()
        vc.pause()
        print("Pause triggered")
        await ctx.send(embed=discord.Embed(
            description="⏸️ Music paused",
            color=discord.Color.gold()
        ))

    @app_commands.command(name="pause", description="Pause the currently playing song")
    async def pause_slash(self, interaction: Interaction):
        vc = self.music.voice_client
        if not vc or not vc.is_playing():
            return await interaction.response.send_message("Nothing is playing right now.", ephemeral=True)
        if vc.is_paused():
            return await interaction.response.send_message("⏸️ Already paused.", ephemeral=True)

        self.music.pause()
        vc.pause()
        embed = discord.Embed(
            description="⏸️ Music paused",
            color=discord.Color.gold()
        )
        await interaction.response.send_message(embed=embed)
        

async def setup(bot):
    await bot.add_cog(Pause(bot))