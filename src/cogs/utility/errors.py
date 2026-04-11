import discord
from discord.ext import commands

class GlobalErrors(commands.Cog):
    """Global error handler for clean user feedback."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        # Ignore typos gracefully
        if isinstance(error, commands.CommandNotFound):
            return

        embed = discord.Embed(title="❌ Error", color=discord.Color.red())

        if isinstance(error, commands.MissingPermissions):
            missing = ", ".join(error.missing_permissions)
            embed.description = f"You lack the required permissions to run this command: `{missing}`"
        elif isinstance(error, commands.BotMissingPermissions):
            missing = ", ".join(error.missing_permissions)
            embed.description = f"I lack the required permissions to do that: `{missing}`"
        elif isinstance(error, commands.MissingRequiredArgument):
            embed.description = f"Missing a required argument: `{error.param.name}`\nCheck `/help` for usage."
        elif isinstance(error, commands.BadArgument):
            embed.description = "You provided an invalid argument. Please check the expected format."
        else:
            embed.description = f"An unexpected error occurred.\n`{str(error)}`"
            # Explicit traceback on console for extreme debugging
            print(f"Unhandled Command Error: {error}")

        try:
            await ctx.send(embed=embed, ephemeral=True) # Ephemeral works if slash deferred, standard message if prefix
        except discord.errors.InteractionResponded:
            await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(GlobalErrors(bot))
