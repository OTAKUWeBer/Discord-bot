# commands/slap.py
import discord
from discord.ext import commands
from discord import app_commands, Interaction
import aiohttp
import random

API_RANDOM = "https://g.tenor.com/v1/random?q=hard-slap-anime&key=LIVDSRZULELA&limit=1"

class Slap(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def get_slap_gif(self) -> str | None:
        async with aiohttp.ClientSession() as session:
            async with session.get(API_RANDOM) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return random.choice(data["results"])["url"]
        return None

    @commands.command(name="slap")
    async def slap(self, ctx: commands.Context, user: discord.Member):
        gif = await self.get_slap_gif()
        if gif:
            await ctx.send(f"{ctx.author.mention} [slapped]({gif}) :hand_splayed: {user.mention}")
        else:
            await ctx.send(f"{ctx.author.mention} slapped {user.mention} :hand_splayed:\n(Couldn't fetch GIF)")

    @app_commands.command(name="slap", description="Slap a member")
    async def slash_slap(self, interaction: Interaction, user: discord.Member):
        """Slash command: /slap @user"""
        gif = await self.get_slap_gif()
        if gif:
            await interaction.response.send_message(
                f"{interaction.user.mention} [slapped]({gif}) :hand_splayed: {user.mention}"
            )
        else:
            await interaction.response.send_message(
                f"{interaction.user.mention} slapped {user.mention} :hand_splayed:\n(Couldn't fetch GIF)"
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(Slap(bot))
