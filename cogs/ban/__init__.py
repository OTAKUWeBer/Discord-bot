async def setup(bot):
    await bot.load_extension("cogs.ban.ban")
    await bot.load_extension("cogs.ban.unban")
