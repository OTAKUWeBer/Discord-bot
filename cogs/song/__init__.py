from .music_state import MusicState
from .play import Play
from .pause import Pause
from .skip import Skip
from .help import Help
from .resume import Resume
from .queue import Queue
from .now_playing import NowPlaying
from .stop import Stop

async def setup(bot):
    music_state = MusicState(bot)
    await bot.add_cog(Play(bot, music_state))
    await bot.add_cog(Pause(bot, music_state))
    await bot.add_cog(Skip(bot, music_state))
    await bot.add_cog(Help(bot, music_state))
    await bot.add_cog(Resume(bot, music_state))
    await bot.add_cog(Queue(bot, music_state))
    await bot.add_cog(NowPlaying(bot, music_state))
    await bot.add_cog(Stop(bot, music_state))