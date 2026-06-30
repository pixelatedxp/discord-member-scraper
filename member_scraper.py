import json
import os
import sys
import re
import asyncio
import discord
from discord.ext import commands

CONFIG_PATH = "config.json"
FETCH_MEMBER_DELAY = 0.45
TOKEN_PATTERN = r'[MNO][a-zA-Z\d_-]{23,25}\.[a-zA-Z\d_-]{6}\.[a-zA-Z\d_-]{27}'

bot = commands.Bot(command_prefix="?", self_bot=True)
stop = False

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def log(msg: str):
    print(f"[+] {msg}")


def err(msg: str):
    print(f"[-] {msg}")


def load_config():
    if not os.path.exists(CONFIG_PATH):
        return None
    try:
        with open(CONFIG_PATH, 'r') as f:
            cfg = json.load(f)
        required = ["token", "guild_id", "welcome_channel_id", "only_members", "stop_early", "message_depth"]
        if not all(k in cfg for k in required):
            err("Config file is missing fields. Run interactively or fix config.json.")
            return None
        log(f"Loaded config from {CONFIG_PATH}")
        return cfg
    except (json.JSONDecodeError, IOError) as e:
        err(f"Failed to load config: {e}")
        return None


def save_config(cfg: dict):
    try:
        with open(CONFIG_PATH, 'w') as f:
            json.dump(cfg, f, indent=2)
        log(f"Config saved to {CONFIG_PATH}")
    except IOError as e:
        err(f"Failed to save config: {e}")


def init_scrape_progress(guild_id: str):
    data = {'user-ids': [], 'current-channel': None, 'current-message': None}
    path = f"{guild_id}.json"
    if not os.path.exists(path):
        with open(path, 'w') as f:
            json.dump(data, f)
        log(f"Created progress file {path}.")
    elif os.path.getsize(path) == 0:
        log("Progress file exists but is empty. Refilling.")
        with open(path, 'w') as f:
            json.dump(data, f)
    else:
        log("Progress file exists.")


def get_inputs():
    guild_id = input("[?] Input the Guild ID that will be scraped for user ids: ")
    if not guild_id.strip().isnumeric():
        err("Invalid Guild ID: Non numeric input.")
        sys.exit(1)

    welcome_channel_id = input("[?] ID of the welcome channel (type a letter if there is none): ")
    if not welcome_channel_id.strip().isnumeric():
        log("Welcome channel id isn't valid, will assume there is none.")
        welcome_channel_id = None

    fetch_question = input("[?] Save only current server members? [Y/n]: ")
    only_members = fetch_question.lower().startswith("y")

    stop_question = input("[?] Stop within 150 members of cache? [Y/n]: ")
    stop_early = stop_question.lower().startswith("y")

    depth_raw = input("[?] How many messages deep per channel (1000-40000, 'n' for no limit): ")
    message_depth = parse_depth(depth_raw)

    user_token = input("[?] Input user token: ")
    if not re.match(TOKEN_PATTERN, user_token):
        err("Bad User Token format detected.")
        answer = input("[?] Continue with bad token? [Yes/No]: ").lower().strip()
        if answer != "yes":
            sys.exit(1)

    return guild_id, welcome_channel_id, only_members, stop_early, message_depth, user_token


def parse_depth(raw: str):
    raw = raw.replace(",", "").replace(".", "").strip().lower()
    if raw == "n":
        return None
    if not raw.isnumeric():
        log("Invalid input, defaulting to 1000.")
        return 1000
    val = int(raw)
    if val < 1000:
        log("Defaulting to 1000 depth.")
        return 1000
    if val > 40000:
        log("Defaulting to 40000 depth.")
        return 40000
    log(f"Using depth {val}.")
    return val


async def scrape_messages(guild, channel, mes_depth, is_welcome, curr_member_list, not_in_guild_list, only_members, before=None):
    curr_message = None
    history = channel.history(limit=mes_depth, before=before) if before else channel.history(limit=mes_depth)
    async for message in history:
        if message.author.id in curr_member_list and not (is_welcome and message.author.bot):
            continue
        if message.author.id in not_in_guild_list and not (is_welcome and message.author.bot):
            continue
        try:
            curr_message = message.id
            if not message.author.bot:
                if only_members:
                    await guild.fetch_member(message.author.id)
                    await asyncio.sleep(FETCH_MEMBER_DELAY)
                log(f"New member added: {message.author.name} | Count: {len(curr_member_list) + 1}")
                curr_member_list.append(message.author.id)

            if is_welcome and message.author.bot:
                for mention in message.mentions:
                    if only_members:
                        await guild.fetch_member(mention.id)
                        await asyncio.sleep(FETCH_MEMBER_DELAY)
                    if mention.id not in curr_member_list:
                        log(f"New member from welcome bot mention: {mention.name} | Count: {len(curr_member_list) + 1}")
                        curr_member_list.append(mention.id)
        except discord.NotFound:
            not_in_guild_list.append(message.author.id)
        except (discord.Forbidden, discord.HTTPException) as e:
            err(f"Failed to fetch user: {e}.")
    return curr_message


async def get_top_channels(guild, member, channels, top_n=5):
    ratings = {}
    for ch in channels:
        if ch.type in (discord.ChannelType.category, discord.ChannelType.forum):
            continue
        if not ch.permissions_for(member).read_messages:
            continue
        count = sum(1 for role in guild.roles if ch.permissions_for(role).read_messages)
        ratings[ch.id] = count
    sorted_ratings = sorted(ratings.items(), key=lambda x: x[1], reverse=True)
    result = []
    for ch_id, _ in sorted_ratings[:top_n]:
        try:
            result.append(await guild.fetch_channel(ch_id))
        except (discord.Forbidden, discord.HTTPException) as e:
            err(f"Failed to fetch channel {ch_id}: {e} (skipping).")
    return result


async def build_channel_list(guild, member, tep, welcome_channel_id):
    channels_to_scrape = []
    for ch in tep:
        if ch.type == discord.ChannelType.category:
            continue
        if not ch.permissions_for(member).read_messages:
            continue
        channels_to_scrape.append(ch)
        if ch.type == discord.ChannelType.text:
            try:
                async for thread in ch.archived_threads(limit=None):
                    channels_to_scrape.append(thread)
            except Exception:
                pass
            for thread in ch.threads:
                channels_to_scrape.append(thread)

    if welcome_channel_id:
        wid = int(welcome_channel_id)
        if not any(ch.id == wid for ch in channels_to_scrape):
            try:
                wc = await guild.fetch_channel(wid)
                if wc.type != discord.ChannelType.category:
                    channels_to_scrape.insert(0, wc)
                    log(f"Force-added welcome channel: {wc.name}")
                else:
                    log("Welcome channel is a category, skipping.")
            except Exception as e:
                err(f"Could not fetch welcome channel: {e}.")

    return channels_to_scrape


@bot.event
async def on_ready():
    log(f"Logged in as {bot.user.name} in {len(bot.guilds)} guilds.")
    guild_obj = await fetch_guild_by_id(guild_id)
    if guild_obj:
        await scrape_users(guild_obj)


async def fetch_guild_by_id(gid: str):
    if not gid.strip().isnumeric():
        err("Invalid guild ID.")
        return None
    try:
        guild = await bot.fetch_guild(int(gid))
        log(f"Scraping guild {guild.name}")
        return guild
    except discord.Forbidden:
        err("Failed to fetch guild: No access.")
    except discord.HTTPException:
        err("Failed to fetch guild: HTTP Exception.")
    return None


async def scrape_users(guild: discord.Guild):
    global stop
    init_scrape_progress(str(guild.id))

    member = await guild.fetch_member(bot.user.id)

    try:
        channels = await guild.fetch_channels()
    except (discord.InvalidData, discord.HTTPException) as e:
        err(f"Failed to fetch guild channels: {e}.")
        channels = None

    good_channels = await get_top_channels(guild, member, channels) if channels else []

    with open(f"{guild.id}.json", 'r') as f:
        data = json.load(f)

    curr_member_list = data['user-ids']
    curr_channel_id = data.get('current-channel')
    curr_message_id = data.get('current-message')

    if good_channels:
        try:
            fetched = await guild.fetch_members(
                channels=good_channels, force_scraping=True, delay=0.1, cache=True
            )
            for m in fetched:
                if m.id != bot.user.id:
                    curr_member_list.append(m.id)
        except Exception as e:
            err(f"Error during member scraping: {e}")
            log("Continuing with message scraping...")
    else:
        log("No valid channels for member scraping, continuing with message scraping...")

    new_channels = await guild.fetch_channels()
    tep = []
    for ch in new_channels:
        try:
            tep.append(await guild.fetch_channel(ch.id))
        except discord.Forbidden:
            err(f"Failed to fetch channel {ch.name}: Forbidden.")
            continue

    channels_to_scrape = await build_channel_list(guild, member, tep, welcome_channel_id)
    log(f"Channels to scrape: {len(channels_to_scrape)}")

    not_in_guild_list = []
    curr_channel = None
    curr_message = None
    find_curr_channel = bool(curr_channel_id)
    find_curr_message = bool(curr_message_id)

    try:
        for ch in channels_to_scrape:
            if find_curr_channel:
                if ch.id != curr_channel_id:
                    continue
                find_curr_channel = False
                log("Found the last channel!")

            curr_channel = ch.id
            mes_depth = message_depth
            is_welcome_ch = bool(welcome_channel_id and ch.id == int(welcome_channel_id))

            if is_welcome_ch:
                mes_depth = None
                log(f"Scraping welcome channel: {ch.name}")

            if stop_early and guild.member_count > 250:
                if guild.member_count - len(curr_member_list) < 151:
                    stop = True
                    break

            log(f"Scraping channel {ch.name} for members.")

            if find_curr_message:
                try:
                    before_msg = await ch.fetch_message(curr_message_id)
                    curr_message = await scrape_messages(
                        guild, ch, mes_depth, is_welcome_ch, curr_member_list, not_in_guild_list, only_members, before=before_msg
                    )
                except discord.NotFound:
                    err("Couldn't find the last message.")
                    curr_message = await scrape_messages(
                        guild, ch, mes_depth, is_welcome_ch, curr_member_list, not_in_guild_list, only_members
                    )
                except (discord.Forbidden, discord.HTTPException) as e:
                    err(f"Failed to find last message: {e}.")
                    curr_message = await scrape_messages(
                        guild, ch, mes_depth, is_welcome_ch, curr_member_list, not_in_guild_list, only_members
                    )
            else:
                curr_message = await scrape_messages(
                    guild, ch, mes_depth, is_welcome_ch, curr_member_list, not_in_guild_list, only_members
                )

        label = "members" if only_members else "users"
        log(f"Scraped {len(curr_member_list)} {label}, saving to {guild.id}.json.")
        log(f"Server cache reports {guild.member_count} current members.")
        data['user-ids'] = curr_member_list
        stop = True
        with open(f"{guild.id}.json", 'w') as f:
            json.dump(data, f)

    except Exception as e:
        err(f"Failed: {e}")
        save_progress(guild.id, curr_member_list, curr_channel, curr_message)
    finally:
        if not stop:
            save_progress(guild.id, curr_member_list, curr_channel, curr_message)
            log("Restarting in 5 seconds.")
            await asyncio.sleep(5)
            await scrape_users(guild=guild)


def save_progress(guild_id, member_list, channel, message):
    data = {
        'user-ids': member_list,
        'current-channel': channel,
        'current-message': message,
    }
    with open(f"{guild_id}.json", 'w') as f:
        json.dump(data, f)
    log(f"Progress saved to {guild_id}.json.")


def main():
    global guild_id, welcome_channel_id, only_members, stop_early, message_depth, user_token

    cfg = load_config()
    if cfg and cfg.get("auto_start"):
        log("Auto-start enabled, using saved config.")
        guild_id = cfg["guild_id"]
        welcome_channel_id = cfg["welcome_channel_id"]
        only_members = cfg["only_members"]
        stop_early = cfg["stop_early"]
        message_depth = cfg["message_depth"]
        user_token = cfg["token"]
        bot.run(user_token)
        return

    if cfg:
        answer = input("[?] Use saved config? [Y/n]: ").lower().strip()
        if answer in ("", "y", "yes"):
            guild_id = cfg["guild_id"]
            welcome_channel_id = cfg["welcome_channel_id"]
            only_members = cfg["only_members"]
            stop_early = cfg["stop_early"]
            message_depth = cfg["message_depth"]
            user_token = cfg["token"]
            bot.run(user_token)
            return

    guild_id, welcome_channel_id, only_members, stop_early, message_depth, user_token = get_inputs()

    save_ans = input("[?] Save these settings to config.json? [Y/n]: ").lower().strip()
    if save_ans in ("", "y", "yes"):
        save_config({
            "token": user_token,
            "guild_id": guild_id,
            "welcome_channel_id": welcome_channel_id,
            "only_members": only_members,
            "stop_early": stop_early,
            "message_depth": message_depth,
            "auto_start": False
        })

    bot.run(user_token)


if __name__ == "__main__":
    main()
