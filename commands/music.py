import discord
from discord.ext import commands
from discord import app_commands, Interaction, FFmpegOpusAudio
import yt_dlp
import asyncio
import functools

# Suppress yt_dlp bug report messages
yt_dlp.utils.bug_reports_message = lambda: ''

# yt_dlp options for audio extraction
YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  # IPv4 fix
}

# ffmpeg options for streaming
FFMPEG_OPTIONS = {
    'options': '-vn',
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
}

class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.queue: list[dict] = []
        self.current: dict | None = None
        self.voice_client: discord.VoiceClient | None = None
        self.text_channel: discord.TextChannel | None = None
        self.auto_disconnect_task: asyncio.Task | None = None
        self.skipped = False

    async def get_ytdl_info(self, query: str) -> dict:
        """Asynchronously extract info using yt_dlp in a threadpool."""
        loop = asyncio.get_running_loop()
        url = query if query.startswith(("http://", "https://", "www.")) else f"ytsearch1:{query}"
        fn = functools.partial(
            yt_dlp.YoutubeDL(YTDL_OPTIONS).extract_info,
            url,
            False
        )
        info = await loop.run_in_executor(None, fn)
        if 'entries' in info and info['entries']:
            info = info['entries'][0]
        return info

    async def _play_next(self, error: Exception | None = None):
        if error:
            print(f"Player error: {error}")

        # Only show finished message if not skipped
        if self.current and self.text_channel and not self.skipped:
            embed = discord.Embed(
                description=f"✅ Finished playing: [{self.current['title']}]({self.current['webpage_url']})",
                color=discord.Color.green()
            )
            await self.text_channel.send(embed=embed)
        self.skipped = False

        if self.queue:
            self.current = self.queue.pop(0)
            self.current['start_time'] = self.bot.loop.time()

            # Start buffering via Opus before sending the embed
            source = await FFmpegOpusAudio.from_probe(
                self.current['url'],
                before_options=FFMPEG_OPTIONS['before_options'],
                options=FFMPEG_OPTIONS['options']
            )
            self.voice_client.play(
                source,
                after=lambda e: asyncio.run_coroutine_threadsafe(self._play_next(e), self.bot.loop)
            )

            # Now tell the channel what's playing
            embed = discord.Embed(
                title="🎶 Now Playing",
                description=f"[{self.current['title']}]({self.current['webpage_url']})",
                color=discord.Color.blue()
            )
            await self.text_channel.send(embed=embed)

        else:
            self.current = None
            if self.text_channel:
                embed = discord.Embed(
                    description="⏹️ No more tracks in the queue",
                    color=discord.Color.dark_grey()
                )
                await self.text_channel.send(embed=embed)

    async def join_user_vc(self, user) -> discord.VoiceClient | None:
        voice_state = user.voice
        if not voice_state or not voice_state.channel:
            return None
        channel = voice_state.channel

        if not channel.guild.voice_client:
            vc = await channel.connect(self_deaf=True)
        else:
            vc = channel.guild.voice_client
            await vc.guild.change_voice_state(channel=vc.channel, self_deaf=True)

        self.voice_client = vc
        if self.auto_disconnect_task:
            self.auto_disconnect_task.cancel()
        self.auto_disconnect_task = self.bot.loop.create_task(self.auto_disconnect())
        return vc

    async def auto_disconnect(self):
        try:
            while self.voice_client and self.voice_client.is_connected():
                channel = self.voice_client.channel
                non_bots = [m for m in channel.members if not m.bot]

                if not non_bots:
                    await asyncio.sleep(60)
                    non_bots = [m for m in channel.members if not m.bot]
                    if not non_bots and self.voice_client.is_connected():
                        await self.voice_client.disconnect()
                        break

                if not self.voice_client.is_playing() and self.current is None:
                    await asyncio.sleep(60)
                    if not self.voice_client.is_playing() and self.current is None:
                        await self.voice_client.disconnect()
                        break

                await asyncio.sleep(10)
        except asyncio.CancelledError:
            return

    # ─── HELP ────────────────────────────────────────────────────────────────────

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

    # ─── PLAY ────────────────────────────────────────────────────────────────────

    @commands.command(name="play", help="Play music from YouTube URL or search by song name")
    async def play(self, ctx: commands.Context, *, query: str):
        vc = await self.join_user_vc(ctx.author)
        if not vc:
            return await ctx.send("You aren't in any voice channel!")

        async with ctx.typing():
            try:
                info = await self.get_ytdl_info(query)
            except Exception:
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
        self.queue.append(song)
        self.text_channel = ctx.channel

        embed = discord.Embed(
            description=f"➕ Added to queue: [{song['title']}]({song['webpage_url']})",
            color=discord.Color.green()
        )

        if not vc.is_playing():
            asyncio.run_coroutine_threadsafe(self._play_next(None), self.bot.loop)
        else:
            await ctx.send(embed=embed)

    @app_commands.command(name="play", description="Play music from YouTube URL or song name")
    async def play_slash(self, interaction: Interaction, *, query: str):
        vc = await self.join_user_vc(interaction.user)
        if not vc:
            return await interaction.response.send_message("You aren't in any voice channel!", ephemeral=True)

        await interaction.response.defer(thinking=True)
        try:
            info = await self.get_ytdl_info(query)
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
        self.queue.append(song)
        self.text_channel = interaction.channel  # type: ignore

        embed = discord.Embed(
            description=f"➕ Added to queue: [{song['title']}]({song['webpage_url']})",
            color=discord.Color.green()
        )

        if not vc.is_playing():
            asyncio.run_coroutine_threadsafe(self._play_next(None), self.bot.loop)
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(embed=embed)

    # ─── SKIP ────────────────────────────────────────────────────────────────────

    @commands.command(name="skip", help="Skip the currently playing song")
    async def skip(self, ctx: commands.Context):
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send("You aren't in any voice channel!")
        if self.voice_client and self.voice_client.is_playing():
            self.skipped = True
            self.voice_client.stop()
            embed = discord.Embed(
                description="⏭️ Song skipped!",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)

    @app_commands.command(name="skip", description="Skip current song")
    async def skip_slash(self, interaction: Interaction):
        if not interaction.user.voice or not interaction.user.voice.channel:
            return await interaction.response.send_message("You aren't in any voice channel!", ephemeral=True)
        if self.voice_client and self.voice_client.is_playing():
            self.skipped = True
            self.voice_client.stop()
            embed = discord.Embed(
                description="⏭️ Song skipped!",
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed)

    # ─── PAUSE & RESUME ─────────────────────────────────────────────────────────

    @commands.command(name="pause", help="Pause the currently playing song")
    async def pause(self, ctx: commands.Context):
        if not self.voice_client or not self.voice_client.is_playing():
            return await ctx.send("Nothing is playing right now.")
        self.voice_client.pause()
        embed = discord.Embed(
            description="⏸️ Music paused",
            color=discord.Color.gold()
        )
        await ctx.send(embed=embed)

    @app_commands.command(name="pause", description="Pause the currently playing song")
    async def pause_slash(self, interaction: Interaction):
        if not self.voice_client or not self.voice_client.is_playing():
            return await interaction.response.send_message("Nothing is playing right now.", ephemeral=True)
        self.voice_client.pause()
        embed = discord.Embed(
            description="⏸️ Music paused",
            color=discord.Color.gold()
        )
        await interaction.response.send_message(embed=embed)

    @commands.command(name="resume", help="Resume a paused song")
    async def resume(self, ctx: commands.Context):
        if not self.voice_client or not self.voice_client.is_paused():
            return await ctx.send("No track is paused.")
        self.voice_client.resume()
        embed = discord.Embed(
            description="▶️ Music resumed",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)

    @app_commands.command(name="resume", description="Resume a paused song")
    async def resume_slash(self, interaction: Interaction):
        if not self.voice_client or not self.voice_client.is_paused():
            return await interaction.response.send_message("No track is paused.", ephemeral=True)
        self.voice_client.resume()
        embed = discord.Embed(
            description="▶️ Music resumed",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed)

    # ─── STOP ────────────────────────────────────────────────────────────────────

    @commands.command(name="stop", help="Stop music, clear queue, and disconnect")
    async def stop(self, ctx: commands.Context):
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send("You aren't in any voice channel!")
        self.queue.clear()
        if self.voice_client:
            self.voice_client.stop()
            await self.voice_client.disconnect()
            if self.auto_disconnect_task:
                self.auto_disconnect_task.cancel()
            embed = discord.Embed(
                description="⏹️ Music stopped and queue cleared",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @app_commands.command(name="stop", description="Stop music and clear queue")
    async def stop_slash(self, interaction: Interaction):
        if not interaction.user.voice or not interaction.user.voice.channel:
            return await interaction.response.send_message("You aren't in any voice channel!", ephemeral=True)
        self.queue.clear()
        if self.voice_client:
            self.voice_client.stop()
            await self.voice_client.disconnect()
            if self.auto_disconnect_task:
                self.auto_disconnect_task.cancel()
            embed = discord.Embed(
                description="⏹️ Music stopped and queue cleared",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)

    # ─── QUEUE ───────────────────────────────────────────────────────────────────

    @commands.command(name="queue", help="Show current music queue")
    async def show_queue(self, ctx: commands.Context):
        embed = discord.Embed(title="🎶 Music Queue", color=discord.Color.blurple())
        if self.current:
            embed.add_field(
                name="Now Playing",
                value=f"[{self.current['title']}]({self.current['webpage_url']})",
                inline=False
            )
        if self.queue:
            queue_list = "\n".join(
                f"{i+1}. [{song['title']}]({song['webpage_url']})" 
                for i, song in enumerate(self.queue)
            )
            embed.add_field(name="Up Next", value=queue_list, inline=False)
        else:
            embed.add_field(name="Up Next", value="Queue is empty", inline=False)
        await ctx.send(embed=embed)

    @app_commands.command(name="queue", description="Show current music queue")
    async def queue_slash(self, interaction: Interaction):
        embed = discord.Embed(title="🎶 Music Queue", color=discord.Color.blurple())
        if self.current:
            embed.add_field(
                name="Now Playing",
                value=f"[{self.current['title']}]({self.current['webpage_url']})",
                inline=False
            )
        if self.queue:
            queue_list = "\n".join(
                f"{i+1}. [{song['title']}]({song['webpage_url']})" 
                for i, song in enumerate(self.queue)
            )
            embed.add_field(name="Up Next", value=queue_list, inline=False)
        else:
            embed.add_field(name="Up Next", value="Queue is empty", inline=False)
        await interaction.response.send_message(embed=embed)

    # ─── NOW PLAYING PROGRESS ────────────────────────────────────────────────────

    @commands.command(name="now_playing", help="Show current song progress")
    async def now_playing_command(self, ctx: commands.Context):
        if not self.current or 'start_time' not in self.current:
            embed = discord.Embed(
                description="❌ No song is currently playing",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)

        now = self.bot.loop.time()
        elapsed = now - self.current['start_time']
        total = self.current.get('duration', 0)
        elapsed = min(elapsed, total)

        bar_len = 20
        pos = int((elapsed / total) * bar_len) if total else 0
        bar = '▬' * pos + '🔘' + '▬' * (bar_len - pos)

        def fmt(sec: float) -> str:
            m, s = divmod(int(sec), 60)
            return f"{m:02d}:{s:02d}"

        embed = discord.Embed(
            title="🎶 Now Playing",
            description=f"[{self.current['title']}]({self.current['webpage_url']})",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="Progress",
            value=f"{fmt(elapsed)} {bar} {fmt(total)}",
            inline=False
        )
        await ctx.send(embed=embed)

    @app_commands.command(name="now_playing", description="Show current song progress")
    async def now_playing_slash(self, interaction: Interaction):
        if not self.current or 'start_time' not in self.current:
            embed = discord.Embed(
                description="❌ No song is currently playing",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed)

        now = self.bot.loop.time()
        elapsed = now - self.current['start_time']
        total = self.current.get('duration', 0)
        elapsed = min(elapsed, total)

        bar_len = 20
        pos = int((elapsed / total) * bar_len) if total else 0
        bar = '▬' * pos + '🔘' + '▬' * (bar_len - pos)

        def fmt(sec: float) -> str:
            m, s = divmod(int(sec), 60)
            return f"{m:02d}:{s:02d}"

        embed = discord.Embed(
            title="🎶 Now Playing",
            description=f"[{self.current['title']}]({self.current['webpage_url']})",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="Progress",
            value=f"{fmt(elapsed)} {bar} {fmt(total)}",
            inline=False
        )
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))
