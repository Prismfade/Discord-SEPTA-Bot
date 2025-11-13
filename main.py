import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import aiohttp

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

# Fetch SEPTA Regional Rail Status 
async def get_regional_rail_status():
    url = "https://www3.septa.org/api/TrainView/index.php"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return f"Error: SEPTA API returned status {response.status}"

                data = await response.json()

                if not isinstance(data, list) or len(data) == 0:
                    return "No train data available right now."

                # Summarize train status
                trains = []
                for train in data[:10]:  # Limit output to 10 trains
                    line = train.get("line", "Unknown Line")
                    train_id = train.get("trainno", "Unknown Train")
                    delay = train.get("late", 0)
                    status = "on time" if delay == 0 else f"{delay} min late"
                    trains.append(f"🚆 {line} Train {train_id}: {status}")

                return "\n".join(trains)

    except Exception as e:
        return f"Error fetching SEPTA data: {e}"
    
# Fetch SEPTA Lansdale Line Status (Hardcoded Example)
async def get_lansdale_status():
    url = "https://www3.septa.org/api/TrainView/index.php"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return f"Error: SEPTA API returned status {response.status}"

                data = await response.json()

                if not isinstance(data, list) or len(data) == 0:
                    return "No train data available right now."

                # Filter for Lansdale trains (Lansdale hardcoded)
                lansdale_trains = [
                    train for train in data
                    if "lansdale" in train.get("line", "").lower()
                ]

                if not lansdale_trains:
                    return "No Lansdale Line trains found."

                # Summarize only trains that are late
                delayed = []
                for train in lansdale_trains:
                    line = train.get("line", "Unknown Line")
                    train_id = train.get("trainno", "Unknown Train")
                    delay = train.get("late", 0)
                    if delay > 0:
                        delayed.append(f"🚆 {line} Train {train_id}: {delay} min late")

                if not delayed:
                    return "All Lansdale Line trains are on time ✅"

                return "\n".join(delayed[:10])  # Limit output to 10 trains

    except Exception as e:
        return f"Error fetching SEPTA data: {e}"
    
# Fetch SEPTA Line Status by Name 
async def get_line_status(line_name):
    url = "https://www3.septa.org/api/TrainView/index.php"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return f"Error: SEPTA API returned status {response.status}"

                data = await response.json()
                if not isinstance(data, list) or len(data) == 0:
                    return "No train data available right now."

                # Filter for requested line
                matching_trains = [
                    train for train in data
                    if line_name.lower() in train.get("line", "").lower()
                ]

                if not matching_trains:
                    return f"No trains found for '{line_name.title()}' line."

                # Summarize only trains that are late
                delayed = []
                for train in matching_trains:
                    line = train.get("line", "Unknown Line")
                    train_id = train.get("trainno", "Unknown Train")
                    delay = train.get("late", 0)
                    if delay > 0:
                        delayed.append(f"🚆 {line} Train {train_id}: {delay} min late")

                if not delayed:
                    return f"All {line_name.title()} Line trains are on time ✅"

                return "\n".join(delayed[:10])  # Limit to first 10 results

    except Exception as e:
        return f"Error fetching SEPTA data: {e}"


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

    if "!lansdale line status" in content:
        await message.channel.send("Fetching Lansdale Line train status… ")
        status_message = await get_lansdale_status()
        await message.channel.send(status_message)

    elif "!issteptafucked" in content:
        await message.channel.send(
            f"Yeah shit is pretty fucked at 12:04PM \n Don't take the bus nor the train!"
        )

    elif "!thecurrentstatus" in content:
        await message.channel.send(f"the current status is {current_status}\n")

    elif "!regional rail status" in content:
        await message.channel.send("Fetching live SEPTA Regional Rail status… ")
        status_message = await get_regional_rail_status()
        await message.channel.send(status_message)

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

        except Exception as e:
            await message.channel.send("⏰ You didn’t reply in time or an error occurred. Try again.")

    # Allow commands to still work if added later
    await bot.process_commands(message)

# Run Bot 
bot.run(token, log_handler=handler, log_level=logging.INFO)