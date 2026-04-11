import discord
from discord.ext import commands
from discord import app_commands, Interaction
import yt_dlp
import asyncio
import functools

yt_dlp.utils.bug_reports_message = lambda before=';': ''

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
    'source_address': '0.0.0.0', 
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -loglevel quiet'
}

class Music(commands.Cog):
    """Unified Music module for playing, queuing, and controlling audio."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.queue: list[dict] = []
        self.current: dict | None = None
        self.voice_client: discord.VoiceClient | None = None
        self.text_channel: discord.TextChannel | None = None
        self.auto_disconnect_task: asyncio.Task | None = None
        self.skipped = False
        self.is_paused = False
        self.pause_start: float | None = None
        self.total_paused_time: float = 0.0

    # ==========================
    # INTERNAL HELPERS
    # ==========================

    def _trigger_pause(self):
        if not self.is_paused:
            self.is_paused = True
            self.pause_start = self.bot.loop.time()

    def _trigger_resume(self):
        if self.is_paused and self.pause_start is not None:
            paused_duration = self.bot.loop.time() - self.pause_start
            self.total_paused_time += paused_duration
            self.pause_start = None
            self.is_paused = False

    def get_elapsed(self) -> float:
        if not self.current or 'start_time' not in self.current:
            return 0.0
        now = self.bot.loop.time()
        if self.is_paused and self.pause_start is not None:
            return self.pause_start - self.current['start_time'] - self.total_paused_time
        return now - self.current['start_time'] - self.total_paused_time

    async def get_ytdl_info(self, query: str) -> dict:
        loop = asyncio.get_running_loop()
        url = query if query.startswith(("http://", "https://", "www.")) else f"ytsearch1:{query}"
        fn = functools.partial(yt_dlp.YoutubeDL(YTDL_OPTIONS).extract_info, url, False)
        info = await loop.run_in_executor(None, fn)
        if 'entries' in info and info['entries']:
            info = info['entries'][0]
        return info

    async def join_user_vc(self, user) -> discord.VoiceClient | None:
        voice_state = user.voice
        if not voice_state or not voice_state.channel:
            return None
        channel = voice_state.channel

        if not channel.guild.voice_client:
            vc = await channel.connect(self_deaf=True)
        else:
            vc = channel.guild.voice_client
            if getattr(vc, 'channel', None) != channel:
                await vc.move_to(channel)

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
            pass

    async def _play_next(self, error: Exception | None = None):
        if error:
            print(f"Player error: {error}")

        self.is_paused = False
        self.pause_start = None
        self.total_paused_time = 0.0
        
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
            source = discord.FFmpegPCMAudio(
                self.current['url'],
                before_options=FFMPEG_OPTIONS['before_options'],
                options=FFMPEG_OPTIONS['options']
            )
            self.voice_client.play(
                source,
                after=lambda e: asyncio.run_coroutine_threadsafe(self._play_next(e), self.bot.loop)
            )
            embed = discord.Embed(
                title="🎶 Now Playing",
                description=f"[{self.current['title']}]({self.current['webpage_url']})",
                color=discord.Color.blue()
            )
            if self.text_channel:
                await self.text_channel.send(embed=embed)
        else:
            self.current = None
            if self.text_channel:
                embed = discord.Embed(description="⏹️ No more tracks in the queue", color=discord.Color.dark_grey())
                await self.text_channel.send(embed=embed)

    # ==========================
    # COMMANDS
    # ==========================

    @commands.command(name="play", help="Play music from YouTube URL or search")
    async def play(self, ctx: commands.Context, *, query: str):
        await self._execute_play(ctx, ctx.author, ctx.channel, getattr(ctx, "typing"), query)

    @app_commands.command(name="play", description="Play music from YouTube URL or song name")
    async def play_slash(self, interaction: Interaction, query: str):
        async def dummy_typing():
            await interaction.response.defer(thinking=True)
            yield
        
        # Override channel setting inside _execute_play
        class DummyCtxForSlash:
            async def send(self, **kwargs):
                await interaction.followup.send(**kwargs)
                
        await self._execute_play(DummyCtxForSlash(), interaction.user, interaction.channel, dummy_typing, query)

    async def _execute_play(self, ctx_like, user, channel, typing_context_manager, query: str):
        vc = await self.join_user_vc(user)
        if not vc:
            return await ctx_like.send("❌ You aren't in any voice channel!")
            
        async with typing_context_manager():
            try:
                info = await self.get_ytdl_info(query)
            except Exception:
                return await ctx_like.send(embed=discord.Embed(description="❌ Could not find or play anything for that search.", color=discord.Color.red()))

        song = {
            'title': info['title'],
            'url': info['url'],
            'duration': info.get('duration', 0),
            'webpage_url': info.get('webpage_url', info.get('url'))
        }
        self.queue.append(song)
        self.text_channel = channel

        embed = discord.Embed(description=f"➕ Added to queue: [{song['title']}]({song['webpage_url']})", color=discord.Color.green())
        await ctx_like.send(embed=embed)

        if not vc.is_playing() and not self.is_paused:
            asyncio.run_coroutine_threadsafe(self._play_next(None), self.bot.loop)

    @commands.command(name="skip")
    async def skip(self, ctx: commands.Context):
        await self._execute_skip(ctx, ctx.author)

    @app_commands.command(name="skip", description="Skip current song")
    async def skip_slash(self, interaction: Interaction):
        class DummyCtx:
            async def send(self, **kwargs): await interaction.response.send_message(**kwargs)
        await self._execute_skip(DummyCtx(), interaction.user)

    async def _execute_skip(self, ctx_like, user):
        if not user.voice or not user.voice.channel:
            return await ctx_like.send("❌ You aren't in any voice channel!")
        if self.voice_client and self.voice_client.is_playing():
            self.skipped = True
            self.voice_client.stop()
            await ctx_like.send(embed=discord.Embed(description="⏭️ Song skipped!", color=discord.Color.orange()))
        else:
            await ctx_like.send("❌ Nothing is currently playing.")

    @commands.command(name="stop")
    async def stop(self, ctx: commands.Context):
        await self._execute_stop(ctx, ctx.author)

    @app_commands.command(name="stop", description="Stop music and clear queue")
    async def stop_slash(self, interaction: Interaction):
        class DummyCtx:
            async def send(self, **kwargs): await interaction.response.send_message(**kwargs)
        await self._execute_stop(DummyCtx(), interaction.user)

    async def _execute_stop(self, ctx_like, user):
        if not user.voice or not user.voice.channel:
            return await ctx_like.send("❌ You aren't in any voice channel!")
        self.queue.clear()
        if self.voice_client:
            self.voice_client.stop()
            await self.voice_client.disconnect()
            if self.auto_disconnect_task:
                self.auto_disconnect_task.cancel()
            await ctx_like.send(embed=discord.Embed(description="⏹️ Music stopped and queue cleared", color=discord.Color.red()))

    @commands.command(name="pause")
    async def pause(self, ctx: commands.Context):
        await self._execute_pause(ctx)

    @app_commands.command(name="pause", description="Pause the currently playing song")
    async def pause_slash(self, interaction: Interaction):
        class DummyCtx:
            async def send(self, **kwargs): await interaction.response.send_message(**kwargs)
        await self._execute_pause(DummyCtx())

    async def _execute_pause(self, ctx_like):
        if not self.voice_client:
            return await ctx_like.send("❌ Not connected to a voice channel.")
        if self.voice_client.is_paused():
            return await ctx_like.send("⏸️ Already paused.")
        if not self.voice_client.is_playing():
            return await ctx_like.send("❌ Nothing is playing right now.")
        self._trigger_pause()
        self.voice_client.pause()
        await ctx_like.send(embed=discord.Embed(description="⏸️ Music paused", color=discord.Color.gold()))

    @commands.command(name="resume")
    async def resume(self, ctx: commands.Context):
        await self._execute_resume(ctx)

    @app_commands.command(name="resume", description="Resume a paused song")
    async def resume_slash(self, interaction: Interaction):
        class DummyCtx:
            async def send(self, **kwargs): await interaction.response.send_message(**kwargs)
        await self._execute_resume(DummyCtx())

    async def _execute_resume(self, ctx_like):
        if not self.voice_client:
            return await ctx_like.send("❌ Not connected to any voice channel.")
        if not self.voice_client.is_paused():
            return await ctx_like.send("▶️ Nothing is paused currently.")
        self._trigger_resume()
        self.voice_client.resume()
        await ctx_like.send(embed=discord.Embed(description="▶️ Music resumed", color=discord.Color.blue()))

    @commands.command(name="queue")
    async def show_queue(self, ctx: commands.Context):
        await self._execute_queue(ctx)

    @app_commands.command(name="queue", description="Show current music queue")
    async def queue_slash(self, interaction: Interaction):
        class DummyCtx:
            async def send(self, **kwargs): await interaction.response.send_message(**kwargs)
        await self._execute_queue(DummyCtx())

    async def _execute_queue(self, ctx_like):
        embed = discord.Embed(title="🎶 Music Queue", color=discord.Color.blurple())
        if self.current:
            embed.add_field(name="Now Playing", value=f"[{self.current['title']}]({self.current['webpage_url']})", inline=False)
        if self.queue:
            q_list = "\n".join(f"{i+1}. [{s['title']}]({s['webpage_url']})" for i, s in enumerate(self.queue[:10]))
            if len(self.queue) > 10: q_list += "\n...and more"
            embed.add_field(name="Up Next", value=q_list, inline=False)
        else:
            embed.add_field(name="Up Next", value="Queue is empty", inline=False)
        await ctx_like.send(embed=embed)

    @commands.command(name="now_playing")
    async def now_playing(self, ctx: commands.Context):
        await self._send_now_playing(ctx)

    @app_commands.command(name="now_playing", description="Show current song progress")
    async def now_playing_slash(self, interaction: Interaction):
        class DummyCtx:
            async def send(self, **kwargs): await interaction.response.send_message(**kwargs)
        await self._send_now_playing(DummyCtx())

    async def _send_now_playing(self, ctx_like):
        if not self.current or 'start_time' not in self.current:
            return await ctx_like.send(embed=discord.Embed(description="❌ No song is currently playing", color=discord.Color.red()))
        
        elapsed = self.get_elapsed()
        total = self.current.get('duration', 0)
        elapsed = max(0, min(elapsed, total))
        bar_len = 20
        pos = int((elapsed / total) * bar_len) if total else 0
        bar = '▬' * pos + '🔘' + '▬' * (bar_len - pos)

        def fmt(sec: float):
            m, s = divmod(int(sec), 60)
            return f"{m:02d}:{s:02d}"

        embed = discord.Embed(title="🎶 Now Playing", description=f"[{self.current['title']}]({self.current['webpage_url']})", color=discord.Color.blue())
        embed.add_field(name="Progress", value=f"{fmt(elapsed)} {bar} {fmt(total)}", inline=False)
        await ctx_like.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))
