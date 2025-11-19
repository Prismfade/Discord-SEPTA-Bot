import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
from Select_menu import LineView
import os
import aiohttp
from Septa_Api import (
    get_regional_rail_status,
    get_line_status,
    get_next_train,
    stationList, get_station_arrivals,
)
from Stations import normalize_station


COMMAND_LIST = []

def register(cmd_name: str):
    COMMAND_LIST.append(cmd_name)
register("!help")
register("!regional rail status")
register("!check line status")
register("!next train")
register("!stations")
register("!menu")
register("!lines")


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

# Bot Initialization
# use help_command = None so the helpers command won't show up.
bot = commands.Bot(command_prefix='!', intents=intents,help_command = None )



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
            "O I I A I (Best GIF EVER) \n"
        )

@bot.event
async def on_message(message):
    current_status = "Bad , very heavy load"
    if message.author == bot.user:
        return

    content = message.content.lower()

    #      REGIONAL RAIL STATUS       #
    if "!regional rail status" in content:
        await message.channel.send("Fetching live SEPTA Regional Rail status… ")
        status_message = await get_regional_rail_status()
        await message.channel.send(status_message)

    #       CHECK ANY LINE STATUS     #
    elif "!check line status" in content:
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

    elif "!stations" in content:
        await message.channel.send("Fetching all Regional Rail stations…")
        result = await stationList()
        await message.channel.send(result)

    elif "!help" in content:
        help_text = "**Available Commands:**\n\n"

        HELP_DICT = {
            "!help": "Shows this help menu.(You prob already know this but, I like putting it here)",
            "!regional rail status": "Shows live delays for all Regional Rail trains.",
            "!check line status": "Lets you check any specific train line.",
            "!next train": "Shows the next train between two stations.",
            "!stations": "Lists all Regional Rail stations.",
            "!menu":"Shows the list of Regional Rail Line for user to select",
            "!lines": "Shows what lines serve the station",

        }

        for cmd, desc in HELP_DICT.items():
            help_text += f"{cmd} — {desc}\n"

        await message.channel.send(help_text)

    elif "!lines" in content:
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

    # Allow commands to still work if added later
    await bot.process_commands(message)

@bot.command()
async def menu(ctx):
    await ctx.send("Select a regional rail **line**:", view=LineView())

    

# Run Bot
bot.run(token, log_handler=handler, log_level=logging.INFO)

