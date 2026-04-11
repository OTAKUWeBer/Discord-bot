import discord
from discord.ext import commands
from discord import app_commands, Interaction
import json
import os
from datetime import datetime

class Update(commands.Cog):
    """Website Updates reader and manager."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        self.data_dir = os.path.join(self.base_dir, "data")
        os.makedirs(self.data_dir, exist_ok=True)
        self.file_path = os.path.join(self.data_dir, "website_updates.json")
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump([
                    {
                        "date": datetime.utcnow().strftime("%Y-%m-%d"),
                        "version": "1.0.0",
                        "features": [
                            "Initial configuration.",
                            "Bot launched successfully."
                        ]
                    }
                ], f, indent=4)

    def _read_updates(self):
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _write_updates(self, data):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    @commands.command(name="updates", help="See what new features have been added")
    async def updates(self, ctx: commands.Context):
        await self._send_updates(ctx)

    @app_commands.command(name="updates", description="See what new features have been added recently")
    async def updates_slash(self, interaction: Interaction):
        await self._send_updates(interaction)

    async def _send_updates(self, ctx_like):
        data = self._read_updates()
        if not data:
            embed = discord.Embed(description="❌ No updates found.", color=discord.Color.red())
            if hasattr(ctx_like, "send"): return await ctx_like.send(embed=embed)
            else: return await ctx_like.response.send_message(embed=embed)

        embed = discord.Embed(
            title="🌐 Latest Website Updates",
            color=discord.Color.blue()
        )
        
        # Display up to 3 recent updates natively
        for entry in data[:3]:
            features_text = "\n".join(f"- {f}" for f in entry.get("features", []))
            embed.add_field(
                name=f"v{entry.get('version', '?.?')} ({entry.get('date', 'Unknown Date')})",
                value=features_text or "No specific features listed.",
                inline=False
            )
            
        if hasattr(ctx_like, "send"):
            await ctx_like.send(embed=embed)
        else:
            await ctx_like.response.send_message(embed=embed)

    @commands.command(name="addupdate", help="[Admin] Add a website update announcement. Separate features with pipes (|).")
    @commands.has_permissions(administrator=True)
    async def addupdate(self, ctx: commands.Context, version: str, *, features: str):
        self._append_update(version, features)
        await ctx.send(f"✅ Update `v{version}` has been published!")

    @app_commands.command(name="addupdate", description="[Admin] Add a website update. Separate features with pipes (|).")
    @app_commands.checks.has_permissions(administrator=True)
    async def addupdate_slash(self, interaction: Interaction, version: str, features: str):
        self._append_update(version, features)
        await interaction.response.send_message(f"✅ Update `v{version}` has been published!")

    def _append_update(self, version: str, features: str):
        data = self._read_updates()
        # Allows user to pass "Added feature 1 | Fixed bug 2" and formats it cleanly.
        feature_list = [f.strip() for f in features.replace("|", "\n").split("\n") if f.strip()]
        new_entry = {
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "version": version,
            "features": feature_list
        }
        data.insert(0, new_entry) # Put it at the top
        self._write_updates(data)

async def setup(bot: commands.Bot):
    await bot.add_cog(Update(bot))
