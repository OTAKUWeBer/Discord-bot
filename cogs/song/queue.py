import discord
from discord.ext import commands
from discord import app_commands, Interaction
from .music_state import MusicState
import asyncio


class Queue(commands.Cog):
    def __init__(self, bot, music_state):
        self.bot = bot
        self.music = music_state
        
    @commands.command(name="queue", help="Show current music queue")
    async def show_queue(self, ctx: commands.Context):
        embed = discord.Embed(title="🎶 Music Queue", color=discord.Color.blurple())
        if self.music.current:
            embed.add_field(
                name="Now Playing",
                value=f"[{self.music.current['title']}]({self.music.current['webpage_url']})",
                inline=False
            )
        if self.music.queue:
            queue_list = "\n".join(
                f"{i+1}. [{song['title']}]({song['webpage_url']})" 
                for i, song in enumerate(self.music.queue)
            )
            embed.add_field(name="Up Next", value=queue_list, inline=False)
        else:
            embed.add_field(name="Up Next", value="Queue is empty", inline=False)
        await ctx.send(embed=embed)

    @app_commands.command(name="queue", description="Show current music queue")
    async def queue_slash(self, interaction: Interaction):
        embed = discord.Embed(title="🎶 Music Queue", color=discord.Color.blurple())
        if self.music.current:
            embed.add_field(
                name="Now Playing",
                value=f"[{self.music.current['title']}]({self.music.current['webpage_url']})",
                inline=False
            )
        if self.music.queue:
            queue_list = "\n".join(
                f"{i+1}. [{song['title']}]({song['webpage_url']})" 
                for i, song in enumerate(self.music.queue)
            )
            embed.add_field(name="Up Next", value=queue_list, inline=False)
        else:
            embed.add_field(name="Up Next", value="Queue is empty", inline=False)
        await interaction.response.send_message(embed=embed)
        

async def setup(bot):
    await bot.add_cog(Queue(bot))