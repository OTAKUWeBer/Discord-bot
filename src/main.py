import os
import asyncio
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv

import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("DiscordBot")

# Load environment variables from parent directory
load_dotenv(os.path.join(os.path.dirname(BASE_DIR), ".env"))
TOKEN = os.getenv("BOT_TOKEN")
PREFIX = os.getenv("COMMAND_PREFIX", "!!")
ENABLED_COGS_ENV = os.getenv("ENABLED_COGS", "")
DEV_GUILD_ID = os.getenv("DEV_GUILD_ID", "")

class CustomBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix=PREFIX, intents=intents)
        # Remove default help command, we might supply our own in cogs
        self.remove_command('help')

    async def setup_hook(self):
        logger.info("Setting up cogs...")
        # Make the loading selective based on .env
        if ENABLED_COGS_ENV:
            enabled_cogs = [c.strip() for c in ENABLED_COGS_ENV.split(",") if c.strip()]
        else:
            # If not specified, look for packages/modules recursively in cogs/
            logger.warning("No ENABLED_COGS in .env, will discover available cogs dynamically...")
            enabled_cogs = []
            cogs_dir = os.path.join(BASE_DIR, "cogs")
            if os.path.exists(cogs_dir):
                for root, dirs, files in os.walk(cogs_dir):
                    for file in files:
                        if file.endswith(".py") and not file.startswith("__"):
                            rel_dir = os.path.relpath(root, cogs_dir)
                            if rel_dir == ".":
                                module_name = file[:-3]
                            else:
                                module_name = f"{rel_dir.replace(os.sep, '.')}.{file[:-3]}"
                            enabled_cogs.append(module_name)

        # Load identified extensions
        for cog_name in enabled_cogs:
            try:
                # Will load from cogs/<cog_name>.py or cogs/<cog_name>/__init__.py
                extension_path = f"cogs.{cog_name}"
                await self.load_extension(extension_path)
                logger.info(f"Loaded extension: {extension_path}")
            except Exception as e:
                logger.error(f"Failed to load extension {extension_path}: {e}")

        # Slash command sync happens in on_ready where guilds are available

    async def on_ready(self):
        logger.info("="*40)
        logger.info(f"Logged in as: {self.user} (ID: {self.user.id})")
        logger.info(f"Connected to {len(self.guilds)} guilds")
        for g in self.guilds:
            logger.info(f"  → {g.name} (ID: {g.id})")
        logger.info(f"Listening with prefix: '{PREFIX}'")
        logger.info("="*40)

        # Sync slash commands to guild(s) for instant availability
        logger.info("Syncing application commands (slash commands)...")
        target_guild_id = DEV_GUILD_ID

        # Auto-detect if only connected to 1 guild and no DEV_GUILD_ID set
        if not target_guild_id and len(self.guilds) == 1:
            target_guild_id = str(self.guilds[0].id)
            logger.info(f"Auto-detected single guild: {target_guild_id}")

        if target_guild_id:
            guild = discord.Object(id=int(target_guild_id))
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            logger.info(f"Application commands synced to guild {target_guild_id} (instant).")
        else:
            await self.tree.sync()
            logger.info("Application commands synced globally (may take up to 1 hour to propagate).")

async def main():
    if not TOKEN:
        logger.error("Error: BOT_TOKEN is not set in the .env file.")
        return
        
    bot = CustomBot()
    try:
        async with bot:
            await bot.start(TOKEN)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")

if __name__ == "__main__":
    asyncio.run(main())
