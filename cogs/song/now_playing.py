import discord
from discord.ext import commands
from discord import app_commands, Interaction
from .music_state import MusicState

class NowPlaying(commands.Cog):
    def __init__(self, bot, music_state):
        self.bot = bot
        self.music = music_state
        
    @commands.command(name="now_playing", help="Show current song progress")
    async def now_playing_command(self, ctx: commands.Context):
        await self._send_now_playing(ctx)

    @app_commands.command(name="now_playing", description="Show current song progress")
    async def now_playing_slash(self, interaction: Interaction):
        await self._send_now_playing(interaction)

    async def _send_now_playing(self, ctx_or_interaction):
        current = self.music.current
        if not current or 'start_time' not in current:
            embed = discord.Embed(
                description="❌ No song is currently playing",
                color=discord.Color.red()
            )
            if hasattr(ctx_or_interaction, "send"):
                return await ctx_or_interaction.send(embed=embed)
            else:
                return await ctx_or_interaction.response.send_message(embed=embed)

        elapsed = self.music.get_elapsed()  # Use centralized elapsed time

        total = current.get('duration', 0)
        elapsed = max(0, min(elapsed, total))

        bar_len = 20
        pos = int((elapsed / total) * bar_len) if total else 0
        bar = '▬' * pos + '🔘' + '▬' * (bar_len - pos)

        def fmt(sec: float) -> str:
            m, s = divmod(int(sec), 60)
            return f"{m:02d}:{s:02d}"

        embed = discord.Embed(
            title="🎶 Now Playing",
            description=f"[{current['title']}]({current['webpage_url']})",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="Progress",
            value=f"{fmt(elapsed)} {bar} {fmt(total)}",
            inline=False
        )

        if hasattr(ctx_or_interaction, "send"):
            await ctx_or_interaction.send(embed=embed)
        else:
            await ctx_or_interaction.response.send_message(embed=embed)



async def setup(bot):
    await bot.add_cog(NowPlaying(bot))
