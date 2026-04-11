import discord
from discord.ext import commands
from discord import app_commands

class DynamicHelp(commands.Cog):
    """Dynamically generating help command and system ping info."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="help", description="Show all available commands dynamically.")
    async def help_cmd(self, ctx: commands.Context):
        embed = discord.Embed(
            title="📚 Available Commands",
            description="Here are all currently loaded commands organized by module.",
            color=discord.Color.blue()
        )
        
        for cog_name, cog in self.bot.cogs.items():
            # Exclude backend helper cogs if needed
            if cog_name == "GlobalErrors":
                continue
                
            cog_cmds = cog.get_commands()
            if not cog_cmds:
                continue
                
            cmd_list = []
            for cmd in cog_cmds:
                desc = cmd.description or cmd.help or "No description provided."
                # Clean up generic help desc
                if len(desc) > 50: desc = desc[:47] + "..."
                cmd_list.append(f"`/{cmd.name}` - {desc}")
                
            if cmd_list:
                embed.add_field(
                    name=f"🧩 {cog_name}",
                    value="\n".join(cmd_list),
                    inline=False
                )

        embed.set_footer(text=f"Total Extensons Loaded: {len(self.bot.cogs)}")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="ping", aliases=["p"], description="Check the bot's latency.")
    async def ping(self, ctx: commands.Context):
        latency = round(self.bot.latency * 1000)
        await ctx.send(f"🏓 Pong! WebSocket Latency: `{latency}ms`")

async def setup(bot: commands.Bot):
    await bot.add_cog(DynamicHelp(bot))
