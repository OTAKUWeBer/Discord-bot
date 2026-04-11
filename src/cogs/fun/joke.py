import discord
from discord.ext import commands
from discord import app_commands, Interaction
import aiohttp

class Joke(commands.Cog):
    """Fetch jokes from a Joke API."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.api_url = "https://v2.jokeapi.dev/joke/"

    async def fetch_joke(self, category: str) -> str:
        # Construct the URL. Examples: https://v2.jokeapi.dev/joke/Dark
        url = f"{self.api_url}{category}"
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, timeout=5) as resp:
                    if resp.status != 200:
                        return "❌ Failed to fetch a joke. Try again later!"
                    
                    data = await resp.json()
                    
                    if data.get("error"):
                        return "❌ Error parsing the joke from the server."
                    
                    if data.get("type") == "single":
                        return data.get("joke", "")
                    elif data.get("type") == "twopart":
                        setup = data.get("setup", "")
                        delivery = data.get("delivery", "")
                        # Discord spoiler tags for the punchline!
                        return f"{setup}\n\n||{delivery}||"
                    
                    return "❌ Unknown joke format."
            except Exception as e:
                return "❌ Unable to contact the Joke API."

    @commands.command(name="joke", help="Get a joke. Usage: !!joke [category] (Any, Dark, Programming, Pun, Spooky, Christmas)")
    async def joke(self, ctx: commands.Context, category: str = "Dark"):
        valid_categories = ["Any", "Dark", "Programming", "Pun", "Spooky", "Christmas", "Misc"]
        category = category.capitalize()
        if category not in valid_categories:
            category = "Dark" # Default enforcement if they type junk
            
        async with ctx.typing():
            joke_text = await self.fetch_joke(category)
            
        embed = discord.Embed(
            title=f"🎭 {category} Joke", 
            description=joke_text, 
            color=discord.Color.purple()
        )
        await ctx.send(embed=embed)

    @app_commands.command(name="joke", description="Tells a joke")
    @app_commands.describe(category="Select a joke category (default: Dark)")
    @app_commands.choices(category=[
        app_commands.Choice(name="Dark", value="Dark"),
        app_commands.Choice(name="Programming", value="Programming"),
        app_commands.Choice(name="Pun", value="Pun"),
        app_commands.Choice(name="Spooky", value="Spooky"),
        app_commands.Choice(name="Misc", value="Misc"),
        app_commands.Choice(name="Any", value="Any")
    ])
    async def slash_joke(self, interaction: Interaction, category: app_commands.Choice[str] = None):
        actual_category = category.value if category else "Dark"
        
        # Defer since API requests can occasionally take more than 3 seconds
        await interaction.response.defer()
        joke_text = await self.fetch_joke(actual_category)
        
        embed = discord.Embed(
            title=f"🎭 {actual_category} Joke",
            description=joke_text, 
            color=discord.Color.purple()
        )
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Joke(bot))
