import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import aiohttp
from Septa_Api import (
    get_regional_rail_status,
    get_lansdale_status,
    get_line_status,
    get_next_train   # <-- NEW IMPORT
)

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
bot = commands.Bot(command_prefix='!', intents=intents)



# Events 
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    print('------')

@bot.event
async def on_message(message):
    current_status = "Bad , very heavy load"
    if message.author == bot.user:
        return

    content = message.content.lower()

    #      LANSDLE LINE STATUS        #
    if "!lansdale line status" in content:
        await message.channel.send("Fetching Lansdale Line train status… ")
        status_message = await get_lansdale_status()
        await message.channel.send(status_message)

    #      REGIONAL RAIL STATUS       #
    elif "!regional rail status" in content:
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
    elif "!next train" in content:
        def check(m):
            return m.author == message.author and m.channel == message.channel

        # Ask for origin
        await message.channel.send("What station are you getting on at?")

        try:
            origin_msg = await bot.wait_for('message', check=check, timeout=20)
            origin = origin_msg.content.strip()

            # Ask for destination
            await message.channel.send(f"➡️ Where are you going from **{origin.title()}**?")
            dest_msg = await bot.wait_for('message', check=check, timeout=20)
            destination = dest_msg.content.strip()

            await message.channel.send(
                f"Fetching the **next train** from **{origin.title()} → {destination.title()}**…"
            )

            status_message = await get_next_train(origin, destination)
            await message.channel.send(status_message)

        except Exception:
            await message.channel.send("⏰ You didn’t reply in time. Try again.")

    # Allow commands to still work if added later
    await bot.process_commands(message)

# Run Bot 
bot.run(token, log_handler=handler, log_level=logging.INFO)
