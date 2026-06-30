# Discord Member Scraper

Scrapes user IDs from a Discord server via message history, threads, and welcome logs.

**Warning**: This uses a self-bot, which violates Discord's ToS. Your account can be permanently banned. For educational use only.

## Quick Start

```
pip install -r requirements.txt
python member_scraper.py
```

You'll be prompted for:
- Your Discord user token
- The server (guild) ID
- An optional welcome channel ID
- Message depth per channel (1000-40000, or no limit)

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
