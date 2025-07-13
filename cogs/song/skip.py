import discord
from discord.ext import commands
from discord import app_commands, Interaction
from .music_state import MusicState


class Skip(commands.Cog):
    def __init__(self, bot, music_state):
        self.bot = bot
        self.music = music_state
        
    @commands.command(name="skip", help="Skip the currently playing song")
    async def skip(self, ctx: commands.Context):
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send("You aren't in any voice channel!")
        if self.music.voice_client and self.music.voice_client.is_playing():
            self.music.skipped = True
            self.music.voice_client.stop()
            embed = discord.Embed(
                description="⏭️ Song skipped!",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)

    @app_commands.command(name="skip", description="Skip current song")
    async def skip_slash(self, interaction: Interaction):
        if not interaction.user.voice or not interaction.user.voice.channel:
            return await interaction.response.send_message("You aren't in any voice channel!", ephemeral=True)
        if self.music.voice_client and self.music.voice_client.is_playing():
            self.music.skipped = True
            self.music.voice_client.stop()
            embed = discord.Embed(
                description="⏭️ Song skipped!",
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed)
            

async def setup(bot):
    await bot.add_cog(Skip(bot))