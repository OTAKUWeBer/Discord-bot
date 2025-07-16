# banlog.py
import discord
from discord.ext import commands
import os
import csv
from datetime import datetime

LOG_FILE_NAME = "logs.csv"

class BanLog(commands.Cog):
    """View ban/unban history from logs."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="banlog")
    @commands.has_permissions(ban_members=True)
    async def banlog(self, ctx, user_id: int):
        """Check ban/unban history of a user by ID."""
        # File path
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, "ban_logs", LOG_FILE_NAME)

        if not os.path.exists(file_path):
            return await ctx.send("❌ No log file found.")

        logs = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if int(row["user_id"]) == user_id:
                        logs.append(row)
        except Exception as e:
            return await ctx.send(f"⚠️ Error reading logs: {e}")

        if not logs:
            return await ctx.send("📭 No logs found for that user.")

        embed = discord.Embed(
            title=f"📜 Ban History for {user_id}",
            color=discord.Color.orange()
        )

        for entry in logs[-10:]:  # Limit to last 10 entries
            timestamp = entry["timestamp"]
            action = entry["action"]
            mod = entry["moderator"]
            reason = entry["reason"] or "No reason given."
            embed.add_field(
                name=f"{action} at {timestamp}",
                value=f"By: {mod}\nReason: {reason}",
                inline=False
            )

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(BanLog(bot))
