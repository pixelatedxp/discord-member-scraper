# Discord Member Scraper

<div align="center">
  
  **Member Data Collection Tool for Discord Servers**
  
  *Extract user IDs from message history, threads, and welcome logs*
  
  <br>
  
  <div align="center">
    <img src="https://img.shields.io/badge/Python-3.8+-blue.svg">
    <img src="https://img.shields.io/badge/License-MIT-green.svg">
    <img src="https://img.shields.io/badge/Version-1.2.0-yellow.svg">
  </div>
</div>

---

## ⚠️ Important Warning

<div class="warning" align="center">

> **WARNING: This uses a Self-Bot, which is against Discord's rules.**
> 
> Discord doesn't allow automated scripts to run on user accounts.
> 
> **Your account could be permanently banned if detected.**
> 
> *Only use this for educational purposes or on servers you own.*

</div>

---

## What This Does

This script helps you collect user IDs from a Discord server. It goes through all the text channels, looks at old messages, checks threads (even archived ones), and can read welcome messages from bots like Dyno or MEE6.

## Main Features

### What It Collects
- User IDs from all text channels
- Users from active and old threads
- Users mentioned in welcome/entry logs
- Checks if users are still in the server (optional)

### Smart Features
- **Saves Progress**: If the script stops, it can continue where it left off
- **Chooses Best Channels First**: Finds the most active channels automatically
- **Handles Rate Limits**: Won't get you banned from Discord's API
- **Removes Duplicates**: Same user won't be added twice

### Data Output
- Saves everything to a clean JSON file
- Shows progress while working
- Organizes data neatly

---

## Getting Started

### What You Need
- Python 3.8 or newer
- Your Discord account token
- The ID of the server you want to scan

### Quick Setup

```bash
# Download the code
git clone https://github.com/pixelatedxp/discord-scraper.git

# Go to the folder
cd discord-scraper

# Install what you need
pip install discord.py

# Run it
python main.py
```

---

## How To Use

When you run the script, it will ask you a few questions:

### 1. Your Discord Token
You can find it in your browser's developer tools.

### 2. Server ID
The unique number for the Discord server you want to scan.

### 3. Welcome Channel (Optional)
If your server has a welcome channel where new members are announced, put its ID here.

### 4. How Many Messages
How far back to look in each channel. More messages = more users, but takes longer.

### 5. Check Current Members
If you want to verify users are still in the server, say Yes here.

---

## What You Get

The script creates a file named `SERVER_ID.json` that looks like this:

```json
{
  "server_info": {
    "id": "123456789012345678",
    "scanned_on": "2023-12-01",
    "total_users_found": 1250
  },
  "where_to_continue": {
    "current_channel": "112233445566778899",
    "last_message": "998877665544332211"
  },
  "all_user_ids": [
    "123456789012345678",
    "234567890123456789",
    "345678901234567890"
  ]
}
```

---

## How It Works Step-by-Step

### Step 1: Log In
The script connects to Discord using your token.

### Step 2: Check Server
It looks at the server and finds all the text channels.

### Step 3: Sort Channels
It figures out which channels have the most messages and starts with those.

### Step 4: Read Messages
Goes through old messages in each channel and saves user IDs.

### Step 5: Check Threads
Looks at regular threads and archived threads (the ones you don't normally see).

### Step 6: Welcome Messages
If you gave a welcome channel ID, it reads bot messages there too.

### Step 7: Save and Repeat
Saves progress, moves to next channel, continues until done.

---

## If Something Goes Wrong

### Common Problems and Fixes

| Problem | What To Do |
|---------|------------|
| **Can't log in** | Check your token is correct and hasn't expired |
| **No permission** | Make sure your account can see the channels |
| **Too many requests** | The script will wait and try again automatically |
| **Script stopped** | Just run it again - it will continue where it left |

### Continue After Stopping
If the script stops (internet issues, computer sleep, etc.), just run it again. It reads the JSON file and continues from the last message it checked.

---

## Be Careful With Rate Limits

Discord has rules about how fast you can make requests:

- **Don't scan too fast**: The script has built-in delays
- **Be patient**: Large servers take time (hours, not minutes)
- **Watch for errors**: If you see "rate limited" messages, let it wait

---

## Performance Tips

### For Small Servers (under 1,000 members)
- Set message depth to 5,000-10,000
- Should finish in 30-60 minutes

### For Medium Servers (1,000-10,000 members)
- Set message depth to 15,000-25,000
- Might take 2-4 hours

### For Large Servers (10,000+ members)
- Set message depth to 30,000-40,000
- Could take 6+ hours
- Consider running overnight

---

## Technical Details

### What It Needs To Run
- `discord.py` Python library
- Read access to server channels
- Stable internet connection

### Files Created
- `SERVER_ID.json` - Your collected data
- Temporary progress files (deleted when done)

### Memory Usage
- Uses about 50-100MB of RAM
- More for very large servers

---

## Good Practices

1. **Use a separate account** if possible, not your main account
2. **Don't run multiple scrapers** at the same time
3. **Be respectful** - try not to scrape servers you don't own
4. **Try To Keep the data private** - user IDs are sensitive information

---

## FAQ

**Q: Is this legal?**  
A: The code is legal, but using it violates Discord's Terms of Service.

**Q: Will I definitely get banned?**  
A: Not definitely, but it's a risk. Use at your own risk.

**Q: Does it download messages?**  
A: No, only user IDs. No message content is saved.

**Q: Can I scan multiple servers?**  
A: Yes, run it once for each server.

---

## Getting Help

If you have problems:

1. Check the error message
2. Make sure your token is still valid
3. Verify you have access to the server
4. Check Python and discord.py are installed correctly

For bugs or issues, you **may** DM me.
**Discord**: `pixelatedxpert`

---

## Future Plans

Things I might add later:
- Better progress display with estimates
- Option to export to CSV format
- Filtering options (by date, activity, etc.)

---

## About The Developer

Made by **pixelatedxpert**  
GitHub: https://github.com/pixelatedxpert
**Discord**: `pixelatedxpert`

This tool was created for server admins who need to backup their member lists.

---

## License

MIT License - you can use, modify, and share this code, but I'm not responsible if your Discord account gets banned.

---

<div align="center">
  
  **Remember**: Use responsibly and respect others' privacy.
  
  <br>
  
  *Last updated: December 2023*

</div>
