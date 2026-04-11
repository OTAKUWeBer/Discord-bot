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

        logger.info("Syncing application commands (slash commands)...")
        await self.tree.sync()
        logger.info("Application commands synced.")

    async def on_ready(self):
        logger.info("="*40)
        logger.info(f"Logged in as: {self.user} (ID: {self.user.id})")
        logger.info(f"Connected to {len(self.guilds)} guilds")
        logger.info(f"Listening with prefix: '{PREFIX}'")
        logger.info("="*40)

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
