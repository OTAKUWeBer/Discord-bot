import discord
from discord.ext import commands
from discord import app_commands, Interaction, FFmpegOpusAudio
import yt_dlp
import asyncio
import functools

# Suppress yt_dlp bug report messages
yt_dlp.utils.bug_reports_message = lambda before=';': ''

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
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -loglevel quiet'
}


class MusicState(commands.Cog):
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

    def pause(self):
        if not self.is_paused:
            self.is_paused = True
            self.pause_start = self.bot.loop.time()
            print(f"[pause] pause_start set to {self.pause_start}")

    def resume(self):
        if self.is_paused and self.pause_start is not None:
            paused_duration = self.bot.loop.time() - self.pause_start
            self.total_paused_time += paused_duration
            print(f"[resume] paused duration was {paused_duration:.2f}s, total paused now {self.total_paused_time:.2f}s")
            self.pause_start = None
            self.is_paused = False

    def get_elapsed(self) -> float:
        if not self.current or 'start_time' not in self.current:
            return 0.0
        now = self.bot.loop.time()
        if self.is_paused and self.pause_start is not None:
            # When paused, elapsed time = time at which pause was started
            elapsed = self.pause_start - self.current['start_time'] - self.total_paused_time
        else:
            # When playing, elapsed time = now - start_time - total paused time accumulated
            elapsed = now - self.current['start_time'] - self.total_paused_time
        print(f"[get_elapsed] elapsed={elapsed:.2f}, paused={self.is_paused}")
        return elapsed


    async def get_ytdl_info(self, query: str) -> dict:
        print("🔍 Searching yt-dlp with:", query)
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

        self.is_paused = False
        self.pause_start = None
        self.total_paused_time = 0.0
        self.skipped = False
        
        if self.is_paused:
            print("⏸️ Paused — not starting next song")
            return

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
        
async def setup(bot):
    await bot.add_cog(MusicState(bot))