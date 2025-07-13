import discord
from discord.ext import commands
from discord import app_commands, Interaction
import asyncio

class Help(commands.Cog):
    @commands.command(name="music_help", help="Show list of music commands and their usage")
    async def music_help(self, ctx: commands.Context):
        prefix = ctx.prefix
        embed = discord.Embed(title="🎵 Music Commands", color=discord.Color.blue())
        embed.add_field(name="Play", value=f"```{prefix}play <song name or URL>```", inline=False)
        embed.add_field(name="Skip", value=f"```{prefix}skip```", inline=False)
        embed.add_field(name="Pause", value=f"```{prefix}pause```", inline=False)
        embed.add_field(name="Resume", value=f"```{prefix}resume```", inline=False)
        embed.add_field(name="Stop", value=f"```{prefix}stop```", inline=False)
        embed.add_field(name="Queue", value=f"```{prefix}queue```", inline=False)
        embed.add_field(name="Now", value=f"```{prefix}now_playing```", inline=False)
        await ctx.send(embed=embed)

    @app_commands.command(name="music_help", description="Show music commands")
    async def music_slash(self, interaction: Interaction):
        embed = discord.Embed(title="🎵 Music Commands", color=discord.Color.blue())
        embed.add_field(name="/play", value="Play music from YouTube URL or search by song name", inline=False)
        embed.add_field(name="/skip", value="Skip current song", inline=False)
        embed.add_field(name="/pause", value="Pause the currently playing song", inline=False)
        embed.add_field(name="/resume", value="Resume a paused song", inline=False)
        embed.add_field(name="/stop", value="Stop music and clear queue", inline=False)
        embed.add_field(name="/queue", value="Show current music queue", inline=False)
        embed.add_field(name="/now_playing", value="Show current song progress", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        

async def setup(bot):
    await bot.add_cog(Help(bot))