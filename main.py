import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
from Select_menu import LineView, SubscribeLineView, UnsubscribeLineView
from dynamic_station import fetch_line_station_map
from Line_Subscription import get_user_subscriptions, notify_line, user_line_subscriptions
from Stations import normalize_station
import os, random
import asyncio
from Septa_Api import (
    get_regional_rail_status,
    get_line_status,
    get_next_train,
    stationList, 
    get_station_arrivals,
    get_unique_regional_rail_lines
)

COMMAND_LIST = []

def register(cmd_name: str):
    COMMAND_LIST.append(cmd_name)
register("/help")
register("/regional rail status")
register("/check line status")
register("/next train")
register("/stations")
register("/menu")
register("/lines")
register("/subscribe")
register("/unsubscribe")

# Setup 
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

if not token:
    print("Error: DISCORD_TOKEN not found. Check your .env file.")
    exit()

# Logging 
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

# Intents 
intents = discord.Intents.default()
intents.message_content = True  
intents.members = True    

class MyBot(commands.Bot):
    async def setup_hook(self):
        # Start background task properly for discord.py v2.x
        self.bg_task = asyncio.create_task(background_notify_loop(self))


# Bot Initialization
bot = MyBot(command_prefix='!', intents=intents, help_command=None)

# # Events
@bot.event
async def on_ready():
    print("Bot is online!")
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    print('------')

    channel_id = 1437230785072463882
    channel = bot.get_channel(channel_id)

    if channel:
        await channel.send(
            "**👋 Hey! I'm the SEPTA Status Bot.**\n"
            "I can check train delays, next arrivals, and station information.\n"
            "Type **!help** to see what I can do!\n"
        )

@bot.event
async def on_message(message):
    current_status = "Bad , very heavy load"
    if message.author == bot.user:
        return

    content = message.content.lower()

    #      REGIONAL RAIL STATUS       #
    if "/regional rail status" in content:
        await message.channel.send("Fetching live SEPTA Regional Rail status… ")
        status_message = await get_regional_rail_status()
        await message.channel.send(status_message)

    #       CHECK ANY LINE STATUS     #
    elif "/check line status" in content:
        await message.channel.send("Which train line would you like to check? (e.g. Paoli, Trenton, Lansdale)")

        def check(m):
            return m.author == message.author and m.channel == message.channel

        try:
            user_msg = await bot.wait_for('message', check=check, timeout=20)
            line_name = user_msg.content.strip()
            await message.channel.send(f"Fetching {line_name.title()} Line status… ")

            status_message = await get_line_status(line_name)
            await message.channel.send(status_message)

        except Exception:
            await message.channel.send("⏰ You didn’t reply in time or an error occurred. Try again.")

    #       NEXT TRAIN FEATURE        #
    #elif content("!next train"):
    elif content.startswith("!next train"):
        # remove the command and check if user typed origin + destination in same line
        user_input = content.replace("!next train", "").strip()
        parts = user_input.split()

        # user typed both stations (skip asking questions)
        if len(parts) >= 2:
            origin_raw = parts[0]
            dest_raw = " ".join(parts[1:])  # allow multi-word stations later too

            origin_norm = normalize_station(origin_raw)
            dest_norm = normalize_station(dest_raw)

            await message.channel.send(
                f"Fetching the next train from **{origin_norm} → {dest_norm}**…"
            )

            status_message = await get_next_train(origin_norm, dest_norm)
            await message.channel.send(status_message)
            return

        # user did NOT type stations → original step-by-step flow
        def check(m):
            return m.author == message.author and m.channel == message.channel

        # ask for origin station
        await message.channel.send("What station are you getting on at?")

        try:
            origin_msg = await bot.wait_for('message', check=check, timeout=20)
            origin_raw = origin_msg.content.strip()
            origin_norm = normalize_station(origin_raw)

            # typo hint
            if origin_norm.lower() != origin_raw.lower():
                await message.channel.send(f"Did you mean **{origin_norm}**?")

            # ask for destination
            await message.channel.send(f"➡️ Where are you going from **{origin_norm}**?")
            dest_msg = await bot.wait_for('message', check=check, timeout=20)
            dest_raw = dest_msg.content.strip()
            dest_norm = normalize_station(dest_raw)

            # typo hint
            if dest_norm.lower() != dest_raw.lower():
                await message.channel.send(f"Did you mean **{dest_norm}**?")

            # ask if they want corrected names
            await message.channel.send(
                "Use the corrected names?\n"
                f"- {origin_norm}\n"
                f"- {dest_norm}\n"
                "(yes / no)"
            )

            confirm = await bot.wait_for('message', check=check, timeout=15)
            ans = confirm.content.lower()

            # pick which ones to actually use
            if ans.startswith("y"):
                origin_final = origin_norm
                dest_final = dest_norm
            else:
                origin_final = origin_raw
                dest_final = dest_raw

            # fetch train
            await message.channel.send(
                f"Fetching the next train from **{origin_final} → {dest_final}**…"
            )

            status_message = await get_next_train(origin_final, dest_final)
            await message.channel.send(status_message)

        except Exception:
            await message.channel.send("⏰ You didn’t reply in time. Try again.")

    elif "/stations" in content:
        await message.channel.send("Fetching all Regional Rail stations…")
        result = await stationList()
        await message.channel.send(result)

    elif "/subscribe" in content:
        line_names = await get_unique_regional_rail_lines()
        if not line_names: line_names = ["No lines available"]
        await message.channel.send("Select a regional rail line to subscribe:", view=SubscribeLineView(line_names))

    elif "/unsubscribe" in content:
        user_subs = await get_user_subscriptions(message.author.id)
        if not user_subs:
            await message.channel.send("❌ You aren't subscribed to any lines. Use /subscribe instead.")
            return
        await message.channel.send("Select a line to unsubscribe from:", view=UnsubscribeLineView(user_subs))

    elif "/help" in content:
        help_text = "**Available Commands:**\n\n"

        HELP_DICT = {
            "/help": "Shows this help menu.(You prob already know this but, I like putting it here)",
            "/regional rail status": "Shows live delays for all Regional Rail trains.",
            "/check line status": "Lets you check any specific train line.",
            "/next train": "Shows the next train between two stations.",
            "/stations": "Lists all Regional Rail stations.",
            "/menu":"Shows the list of Regional Rail Line for user to select",
            "/lines": "Shows what lines serve the station",
            "/subscribe": "Sign up to receive status updates for a train line.",
            "/unsubscribe": "Stop receiving status updates for a train line."
        }

        for cmd, desc in HELP_DICT.items():
            help_text += f"{cmd} — {desc}\n"

        await message.channel.send(help_text)

    elif "/lines" in content:
        await message.channel.send("Which station do you want to check?")

        def check(m):
            return m.author == message.author and m.channel == message.channel

        try:
            user_msg = await bot.wait_for('message',check =check,timeout = 20)
            station_raw = user_msg.content.strip()
            station_norm = normalize_station(station_raw)

            from Septa_Api import build_station_line_map
            station_map = await build_station_line_map()

            result = await get_station_arrivals(station_norm)
            await message.channel.send(result)

        except Exception:
            await message.channel.send("⏰ You didn’t reply in time. Try again.")

    #dw about this
    elif any(phrase in content for phrase in ["great job", "good bot", "awesome bot", "good job","good work","w cat","awesome cat"]):
        user = message.author.display_name

        responses = [
            f"Thank you, {user}! 😊 I run smoother than SEPTA!",
            f"Thanks, {user}! 🚆 I’m never late… unlike SEPTA 👀",
            f"Appreciate it, {user}! 😄 My code stays on schedule!",
            f"Thank you, {user}! 🤖 I was built different.",
            f"Aww thanks, {user}! 😊 You're the real MVP.",
            f"Thanks, {user}! 🙌 I run cleaner than SEPTA’s tracks!",
            f"Cheers, {user}! 😄 My uptime > SEPTA reliability.",
            f"O I I A I \<\<SPINNING TECHNIQUE\>\>"
        ]

        reply = random.choice(responses)
        await message.channel.send(reply)
        return

    # Allow commands to still work if added later
    await bot.process_commands(message)

@bot.command()
async def menu(ctx):
    # await ctx.send("Select a regional rail **line**:", view=LineView())
    line_map = await fetch_line_station_map()

    await ctx.send(
        "Select a regional rail **line**:",
        view = LineView(line_map)
    )

async def background_notify_loop(bot):
    await bot.wait_until_ready()
    while not bot.is_closed():
        for user_id, subs in user_line_subscriptions.items():
            for line_name in subs:
                try:
                    status = await get_line_status(line_name)
                    if "late" in status.lower() or "delayed" in status.lower():
                        await notify_line(bot, line_name, status)
                except Exception as e:
                    print(f"Error notifying {user_id} for {line_name}: {e}")

        await asyncio.sleep(60)  # TO-DO: Decide how often to refresh? 
                                 # For testing purposes currently refreshes train line status every 60 seconds.

# Run Bot
bot.run(token, log_handler=handler, log_level=logging.INFO)