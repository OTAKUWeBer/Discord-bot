import discord
from discord.ext import commands
from discord import app_commands, Interaction
from .music_state import MusicState


class Stop(commands.Cog):
    def __init__(self, bot, music_state):
        self.bot = bot
        self.music = music_state
    
    @commands.command(name="stop", help="Stop music, clear queue, and disconnect")
    async def stop(self, ctx: commands.Context):
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send("You aren't in any voice channel!")
        self.music.queue.clear()
        if self.music.voice_client:
            self.music.voice_client.stop()
            await self.music.voice_client.disconnect()
            if self.music.auto_disconnect_task:
                self.music.auto_disconnect_task.cancel()
            embed = discord.Embed(
                description="⏹️ Music stopped and queue cleared",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @app_commands.command(name="stop", description="Stop music and clear queue")
    async def stop_slash(self, interaction: Interaction):
        if not interaction.user.voice or not interaction.user.voice.channel:
            return await interaction.response.send_message("You aren't in any voice channel!", ephemeral=True)
        self.music.queue.clear()
        if self.music.voice_client:
            self.music.voice_client.stop()
            await self.music.voice_client.disconnect()
            if self.music.auto_disconnect_task:
                self.music.auto_disconnect_task.cancel()
            embed = discord.Embed(
                description="⏹️ Music stopped and queue cleared",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
            

async def setup(bot):
    await bot.add_cog(Stop(bot))