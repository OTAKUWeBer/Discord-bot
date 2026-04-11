# 🛠️ Selective Discord Bot

A Python-based Discord bot with a robust modular structure, designed for simple deployment and selective feature loading.

## ✨ Features

- **Selective Cog Loading**: Choose exactly which features to enable via the `.env` file.
- **Robust Subclass Architecture**: Built around a custom `commands.Bot` subclass and modern async `setup_hook` initialization.
- **Slash Command Syncing**: Automatically syncs slash commands on startup.
- **Modular Cogs**: Commands are organized in the `cogs/` directory.

## 📁 Project Structure

```
.
├── src/
│   ├── cogs/
│   │   ├── fun/              # Game/misc commands (slap, joke)
│   │   ├── moderation/       # Unified moderation cog (ban, kick, role, logs)
│   │   ├── music/            # Unified music cog (play, queue, stop)
│   │   └── utility/          # Utility cogs (help, updates)
│   └── main.py               # The main entry point for the bot
├── data/                     # JSON databases (e.g., website_updates.json)
├── logs/                     # CSV Moderation logs
├── .env.example              # Template for environment variables
└── README.md
```

## 🧪 Requirements

- Python 3.8+
- pip modules:
  - `discord.py`
  - `python-dotenv`
  - `requests`
  - `PyNaCl`
  - `yt-dlp`

Install all dependencies:

```bash
pip install -r requirements.txt
```

## 🚀 Usage

1. Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env
   ```
2. Fill in your `BOT_TOKEN` inside `.env`.
3. Modify the `ENABLED_COGS` setting if you want to disable specific components. A blank value will attempt to recursively load all default cogs automatically.
4. Run the bot:

```bash
python main.py
```

## ⚙️ Bot Configuration (.env)

```env
BOT_TOKEN=your-token
COMMAND_PREFIX=!!
ENABLED_COGS=fun.slap,fun.joke,utility.help,utility.info,utility.errors,moderation.moderation,music.music,utility.updates
MOD_LOG_CHANNEL_ID=123456789012345678
```

## 🛡️ Security

- All bot credentials are stored locally in the `.env` file and are never committed to version control.