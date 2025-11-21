import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
from Select_menu import LineView
import os
import asyncio

from Septa_Api import (
    get_regional_rail_status,
    get_line_status,
    get_next_train,
    stationList,
    get_station_arrivals,
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
register("!setalertlevel")  # <-- important


# ---------------------------
# ENV + TOKEN
# ---------------------------
load_dotenv()
token = os.getenv("DISCORD_TOKEN")
if not token:
    print("Error: DISCORD_TOKEN not found.")
    exit()

# ---------------------------
# LOGGING
# ---------------------------
handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")

# ---------------------------
# INTENTS (UPDATED)
# ---------------------------
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True  # REQUIRED for UI components (dropdowns/buttons)

# ---------------------------
# BOT
# ---------------------------
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)


# ---------------------------
# LOAD EXTENSIONS
# ---------------------------
async def load_extensions():
    await bot.load_extension("station_alerts")  # your new dropdown-enabled cog


# ---------------------------
# EVENTS
# ---------------------------
@bot.event
async def on_ready():
    print("Bot is online!")
    print(f"Logged in as {bot.user.name} - {bot.user.id}")
    print("------")

    # Persist UI views if needed
    bot.add_view(LineView())  # <- good practice

    # Optional welcome message
    channel_id = 1437230785072463882
    channel = bot.get_channel(channel_id)
    if channel:
        try:
            await channel.send(
                "**👋 Hey! I'm the SEPTA Status Bot.**\n"
                "I can check train delays, next arrivals, station outages, and more.\n"
                "Type **!help** to get started.\n"
            )
        except:
            pass


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    content = message.content.lower()

    # ----------------------------
    # REGIONAL RAIL STATUS
    # ----------------------------
    if "!regional rail status" in content:
        await message.channel.send("Fetching live SEPTA Regional Rail status…")
        status_message = await get_regional_rail_status()
        await message.channel.send(status_message)

    # ----------------------------
    # LINE STATUS
    # ----------------------------
    elif "!check line status" in content:
        await message.channel.send("Which train line would you like to check? (e.g. Paoli)")

        def check(m):
            return m.author == message.author and m.channel == message.channel

        try:
            user_msg = await bot.wait_for("message", check=check, timeout=20)
            line_name = user_msg.content.strip()
            await message.channel.send(f"Fetching {line_name.title()} Line status…")
            result = await get_line_status(line_name)
            await message.channel.send(result)
        except Exception:
            await message.channel.send("⏰ You didn’t reply in time.")

    # ----------------------------
    # NEXT TRAIN
    # ----------------------------
    elif content.startswith("!next train"):
        user_input = content.replace("!next train", "").strip()
        parts = user_input.split()

        if len(parts) >= 2:
            origin = normalize_station(parts[0])
            dest = normalize_station(" ".join(parts[1:]))
            await message.channel.send(f"Fetching next train from **{origin} → {dest}**…")
            result = await get_next_train(origin, dest)
            await message.channel.send(result)
            return

        def check(m):
            return m.author == message.author and m.channel == message.channel

        await message.channel.send("What station are you getting on at?")
        try:
            origin_msg = await bot.wait_for("message", check=check, timeout=20)
            origin = normalize_station(origin_msg.content.strip())

            await message.channel.send(f"➡️ Where are you going from **{origin}**?")
            dest_msg = await bot.wait_for("message", check=check, timeout=20)
            dest = normalize_station(dest_msg.content.strip())

            await message.channel.send(f"Fetching next train from **{origin} → {dest}**…")
            result = await get_next_train(origin, dest)
            await message.channel.send(result)
        except Exception:
            await message.channel.send("⏰ You didn’t reply in time.")

    # ----------------------------
    # STATIONS
    # ----------------------------
    elif "!stations" in content:
        await message.channel.send("Fetching all Regional Rail stations…")
        result = await stationList()
        await message.channel.send(result)

    # ----------------------------
    # HELP
    # ----------------------------
    elif "!help" in content:
        HELP_DICT = {
            "!help": "Shows this help menu.",
            "!regional rail status": "Shows all Regional Rail delays.",
            "!check line status": "Checks a specific train line.",
            "!next train": "Shows the next train between stations.",
            "!stations": "Lists all Regional Rail stations.",
            "!menu": "Shows a clickable selection menu.",
            "!lines": "Shows which lines serve a station.",
            "!setalertlevel": "Opens the alert sensitivity menu.",
        }

        text = "**Available Commands:**\n\n"
        for cmd, desc in HELP_DICT.items():
            text += f"{cmd} — {desc}\n"

        await message.channel.send(text)

    # ----------------------------
    # LINES
    # ----------------------------
    elif "!lines" in content:
        await message.channel.send("Which station do you want to check?")

        def check(m):
            return m.author == message.author and m.channel == message.channel

        try:
            user_msg = await bot.wait_for("message", check=check, timeout=20)
            station = normalize_station(user_msg.content.strip())
            result = await get_station_arrivals(station)
            await message.channel.send(result)
        except Exception:
            await message.channel.send("⏰ You didn’t reply in time.")

    await bot.process_commands(message)


# ---------------------------
# MENU BUTTON COMMAND
# ---------------------------
@bot.command()
async def menu(ctx):
    await ctx.send("Select a regional rail **line**:", view=LineView())


# ---------------------------
# BOT START (CORRECT WAY)
# ---------------------------
async def main():
    async with bot:
        await load_extensions()
        await bot.start(token)

asyncio.run(main())