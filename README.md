# Discord Member Scraper

Scrapes user IDs from a Discord server via message history, threads, and welcome logs.

**Warning**: This uses a self-bot, which violates Discord's ToS. Your account can be permanently banned. For educational use only.

## Config File

Create a `config.json` next to the script to skip prompts on every run:

```json
{
  "token": "your_token_here",
  "guild_id": "123456789",
  "welcome_channel_id": null,
  "only_members": false,
  "stop_early": false,
  "message_depth": 1000,
  "auto_start": false
}
```

- Set `auto_start` to `true` to skip all prompts and start immediately.
- Set `welcome_channel_id` to a channel ID or `null`.
- `message_depth` can be a number (1000-40000) or `null` for no limit.

If no config file exists, you'll be prompted interactively and asked whether to save your settings.

## Quick Start

```
pip install -r requirements.txt
python member_scraper.py
```

## Output

Creates a `{guild_id}.json` file in the current directory:

```json
{
  "user-ids": [123456789, 234567890],
  "current-channel": null,
  "current-message": null
}
```

If the script is interrupted, it saves progress and resumes from where it left off when restarted.

## Features

- Scrapes user IDs from all readable text channels
- Includes active and archived threads
- Optionally reads welcome bot mentions (Dyno, MEE6, etc.)
- Optional member-only filter (fetches each user to confirm they're still in the server)
- Optional early stop when within 150 members of the total member count
- Auto-resumes after failure (5 second delay, retries)

## Requirements

- Python 3.8+
- discord.py-self

## License

MIT
