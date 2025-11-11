import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

# --- Setup ---
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

if not token:
    print("Error: DISCORD_TOKEN not found. Check your .env file.")
    exit()

# --- Logging ---
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

# --- Intents ---
intents = discord.Intents.default()
intents.message_content = True  # REQUIRES ENABLING ON DEV PORTAL
intents.members = True          # REQUIRES ENABLING ON DEV PORTAL

# --- Bot Initialization ---
bot = commands.Bot(command_prefix='!', intents=intents)

# --- Events ---
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    print('------')

@bot.event
async def on_message(message):
    current_status = "Bad , very heavy load"
    # Don't let the bot respond to itself
    if message.author == bot.user:
        return
    
    # Check for the message content in lowercase
    if "!lansdale line status" in message.content.lower():
        await message.channel.send(f'As of September 5th 2025, 5:45pm:\n the Lansdale Line is running 210 minutes late!')

    if "!issteptafucked" in message.content.lower():
        await message.channel.send(f"Yeah shit is pretty fucked at 12:04PM \n Don't take the bus nor the train!")

    if "!thecurrentstatus" in message.content.lower():
        await message.channel.send(f"the current status is {current_status}\n")
    # This is important for running any other commands
    await bot.process_commands(message)





# --- Run Bot ---
# This will send logs to 'discord.log'
bot.run(token, log_handler=handler, log_level=logging.INFO)