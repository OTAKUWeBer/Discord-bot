import os
import glob
import re
import requests
import subprocess
import pathlib
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv

# === Configure logging ===
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# === Utility: Clear terminal screen ===
def clear_screen():
    if os.name == 'nt':  # Windows
        subprocess.run(['cls'], shell=True)
    else:
        subprocess.run(['clear'])

# Ensure centralized config folder exists
def ensure_bots_folder():
    os.makedirs('bots', exist_ok=True)

# === Bot settings/Cogs ===
INTENTS = discord.Intents.all()

def discover_cogs():
    cogs_dir = pathlib.Path("cogs")
    cog_modules = []
    for path in cogs_dir.rglob("*.py"):
        if path.name == "__init__.py":
            # Add the package module itself (e.g., cogs.song)
            module_path = ".".join(path.with_suffix("").parts)
            cog_modules.append(module_path)
        else:
            # Only add file if it's NOT inside a package directory with __init__.py
            # Check if its parent folder contains __init__.py
            if not (path.parent / "__init__.py").exists():
                module_path = ".".join(path.with_suffix("").parts)
                cog_modules.append(module_path)
    return cog_modules


COGS = discover_cogs()

# === Filename sanitization ===
def sanitize_bot_name(name: str, bot_id: str) -> str:
    """
    Replace unsafe filesystem characters and ensure filename isn't empty.
    Falls back to 'bot_<id>' if name sanitizes to empty.
    """
    # Remove control chars and path separators
    name = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '_', name)
    # Replace spaces with underscore
    name = name.strip().replace(' ', '_')
    # Remove any other non-word characters except hyphen and underscore
    name = re.sub(r'[^\w\-_.]', '', name)
    # Truncate to reasonable length
    name = name[:100]
    return name or f"bot_{bot_id}"

# === Helpers for managing bots/*.env files ===
def list_bots():
    return [os.path.splitext(os.path.basename(f))[0] for f in glob.glob("bots/*.env")]

# Add or update bot credentials and prefix
def add_bot():
    token = input("Enter your bot token: ").strip()
    if not token:
        logger.error("❌ Token can’t be empty.")
        return

    prefix = input("Enter command prefix for this bot (default '!!'): ").strip() or "!!"

    # Validate token via Discord API
    try:
        resp = requests.get(
            "https://discord.com/api/v10/users/@me",
            headers={"Authorization": f"Bot {token}"}, timeout=5
        )
    except requests.RequestException as e:
        logger.error(f"❌ Network error: {e}")
        return

    if resp.status_code != 200:
        msg = resp.json().get("message", resp.text) if resp.headers.get('Content-Type','').startswith('application/json') else resp.text
        logger.error(f"❌ Invalid token: {msg}")
        return

    data = resp.json()
    raw_name, bot_id = data.get("username",""), data.get("id","")
    if not raw_name or not bot_id:
        logger.error("❌ Couldn’t fetch bot username or ID.")
        return

    bot_name = sanitize_bot_name(raw_name, bot_id)
    path = os.path.join('bots', f"{bot_name}.env")

    if os.path.exists(path):
        if input(f".env for '{bot_name}' exists. Overwrite? (y/N): ").strip().lower() != 'y':
            logger.error("❌ Aborted, not overwriting existing credentials.")
            return

    # Write token and prefix safely
    try:
        with open(path, 'w') as f:
            f.write(f"BOT_TOKEN={token}\nCOMMAND_PREFIX={prefix}\n")
        os.chmod(path, 0o600)
    except OSError as e:
        logger.error(f"❌ Failed to write credentials: {e}")
        return

    logger.info(f"✅ Saved token and prefix to {path} (Name: {raw_name}, Prefix: '{prefix}')")

# Change prefix for an existing bot

def change_prefix():
    bots = list_bots()
    if not bots:
        logger.info("ℹ️  No bots to update.")
        return

    for i, b in enumerate(bots,1):
        logger.info(f"{i}. {b}")
    try:
        idx = int(input("Select a bot to update prefix (number): ").strip()) - 1
        bot = bots[idx]
    except (ValueError, IndexError):
        logger.error("❌ Invalid selection.")
        return

    path = os.path.join('bots', f"{bot}.env")
    load_dotenv(path)
    token = os.getenv('BOT_TOKEN')

    new_prefix = input(f"Enter new prefix (current '{os.getenv('COMMAND_PREFIX','!!')}'): ").strip() or os.getenv('COMMAND_PREFIX','!!')

    try:
        with open(path, 'w') as f:
            f.write(f"BOT_TOKEN={token}\nCOMMAND_PREFIX={new_prefix}\n")
    except OSError as e:
        logger.error(f"❌ Could not update prefix: {e}")
        return

    logger.info(f"✅ Updated prefix for {bot} to '{new_prefix}'")

# Remove a bot's file
def remove_bot():
    bots = list_bots()
    if not bots:
        logger.info("ℹ️  No bots to remove.")
        return

    for i, name in enumerate(bots,1): logger.info(f"{i}. {name}")
    try:
        idx = int(input("Select a bot to remove (number): ").strip()) - 1
        target = bots[idx]
    except (ValueError, IndexError):
        logger.error("❌ Invalid selection.")
        return

    path = os.path.join('bots', f"{target}.env")
    try:
        os.remove(path)
        logger.info(f"✅ Removed {path}")
    except OSError as e:
        logger.error(f"❌ Could not remove file: {e}")

# Connect and run selected bot with restart loop and reload command
def connect_bot():
    bots = list_bots()
    if not bots:
        logger.info("ℹ️  No bots saved. Please add one first.")
        return

    for i, b in enumerate(bots,1): logger.info(f"{i}. {b}")
    try:
        idx = int(input("Select a bot to connect (number): ").strip()) - 1
        name = bots[idx]
    except (ValueError, IndexError):
        logger.error("❌ Invalid selection.")
        return

    path = os.path.join('bots', f"{name}.env")
    load_dotenv(path)
    token = os.getenv('BOT_TOKEN')
    prefix = os.getenv('COMMAND_PREFIX','!!')
    if not token:
        logger.error(f"❌ No BOT_TOKEN in {path}")
        return

    bot = commands.Bot(command_prefix=prefix, intents=INTENTS)
    bot.remove_command('help')

    @bot.event
    async def on_ready():
        logger.info(f"\n✨ {bot.user} is now online!")
        logger.info(f"• Name:     {bot.user.name}#{bot.user.discriminator}")
        logger.info(f"• Bot ID:   {bot.user.id}")
        logger.info(f"• Servers:  {len(bot.guilds)}")
        logger.info(f"• Members:  {len(set(bot.get_all_members()))}\n")
        for ext in COGS:
            try:
                await bot.load_extension(f"{ext}")
                logger.info(f"  ✅ Loaded cog: {ext}")
            except Exception as e:
                logger.error(f"  ❌ Failed to load {ext}: {e}")
        await bot.tree.sync()
        logger.info("🔄 Slash commands synced.")

    @bot.command(name='reload_cogs')
    async def reload_cogs(ctx):
        """Reload all cogs without restarting the bot."""
        reloaded = []
        for ext in COGS:
            try:
                await bot.reload_extension(f"{ext}")
                reloaded.append(ext)
            except Exception as e:
                logger.error(f"❌ Failed to reload {ext}: {e}")
        await ctx.send(f"🔄 Reloaded cogs: {', '.join(reloaded)}")

    logger.info(f"▶️  Starting bot {name} with prefix '{prefix}'…")
    # Graceful restart loop
    while True:
        try:
            bot.run(token)
            break
        except Exception as e:
            logger.error(f"❌ Bot crashed: {e}")
            if input("Restart bot? (y/N): ").strip().lower() != 'y':
                break

# === Main menu loop with graceful shutdown ===
def main():
    ensure_bots_folder()
    try:
        while True:
            logger.info("\n=== Bot Manager ===")
            logger.info("1. Connect to a saved bot")
            logger.info("2. Add a new bot")
            logger.info("3. Remove a bot")
            logger.info("4. Change bot prefix")
            logger.info("5. Quit")
            choice = input("Choose an option: ").strip()

            if choice == '1':
                clear_screen()
                connect_bot()
            elif choice == '2':
                clear_screen()
                add_bot()
            elif choice == '3':
                clear_screen()
                remove_bot()
            elif choice == '4':
                clear_screen()
                change_prefix()
            elif choice == '5':
                logger.info("Goodbye!")
                break
            else:
                clear_screen()
                logger.error("❌ Invalid option, try 1–5.")
    except KeyboardInterrupt:
        clear_screen()
        logger.info("\n👋 Interrupted. Goodbye!")

if __name__ == '__main__':
    clear_screen()
    main()
