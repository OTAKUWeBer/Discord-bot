import discord
from discord.ext import commands
from discord import app_commands, Interaction
from .music_state import MusicState
import asyncio

class Play(commands.Cog):
    def __init__(self, bot, music_state):
        self.bot = bot
        self.music = music_state 

    @commands.command(name="play", help="Play music from YouTube URL or search by song name")
    async def play(self, ctx: commands.Context, *, query: str):
        vc = await self.music.join_user_vc(ctx.author)
        if not vc:
            return await ctx.send("You aren't in any voice channel!")
        async with ctx.typing():
            try:
                info = await self.music.get_ytdl_info(query)
            except Exception as e:
                print("❌ yt-dlp failed:", e)
                return await ctx.send(
                    embed=discord.Embed(
                        description="❌ Could not find or play anything for that link/search.",
                        color=discord.Color.red()
                    )
                )

        song = {
            'title':       info['title'],
            'url':         info['url'],
            'duration':    info.get('duration', 0),
            'webpage_url': info.get('webpage_url', info.get('url'))
        }
        self.music.queue.append(song)
        self.music.text_channel = ctx.channel

        embed = discord.Embed(
            description=f"➕ Added to queue: [{song['title']}]({song['webpage_url']})",
            color=discord.Color.green()
        )

        if not vc.is_playing() and not self.music.is_paused:
            asyncio.run_coroutine_threadsafe(self.music._play_next(None), self.bot.loop)
        else:
            await ctx.send(embed=embed)

    @app_commands.command(name="play", description="Play music from YouTube URL or song name")
    async def play_slash(self, interaction: Interaction, *, query: str):
        vc = await self.music.join_user_vc(interaction.user)
        if not vc:
            return await interaction.response.send_message("You aren't in any voice channel!", ephemeral=True)

        await interaction.response.defer(thinking=True)
        try:
            info = await self.music.get_ytdl_info(query)
        except Exception:
            return await interaction.followup.send(
                embed=discord.Embed(
                    description="❌ Could not find or play anything for that link/search.",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )
        song = {
            'title':       info['title'],
            'url':         info['url'],
            'duration':    info.get('duration', 0),
            'webpage_url': info.get('webpage_url', info.get('url'))
        }
        self.music.queue.append(song)
        self.music.text_channel = interaction.channel  # type: ignore

        embed = discord.Embed(
            description=f"➕ Added to queue: [{song['title']}]({song['webpage_url']})",
            color=discord.Color.green()
        )

        if not vc.is_playing() and not self.music.is_paused:

            asyncio.run_coroutine_threadsafe(self.music._play_next(None), self.bot.loop)
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(embed=embed)
            
            
async def setup(bot):
    await bot.add_cog(Play(bot))