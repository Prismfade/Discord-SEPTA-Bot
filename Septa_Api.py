import aiohttp

from Stations import REGIONAL_RAIL_STATIONS, normalize_station
# STATIONS_CACHE = []  -> might not need it no more? since i made the whole listing myself
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


# Fetch Next Train Between Two Stations
async def get_next_train(origin, destination):
    #Convert user input(typos,short cuts) into station names
    # Example: "temple", "temple u", "tu" -> "Temple University" , check the Stations.py file where its ALIASES
    origin = normalize_station(origin)
    destination = normalize_station(destination)
    url = f"https://www3.septa.org/api/NextToArrive/index.php?req1={origin}&req2={destination}"
    print("DEBUG URL:", url)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return f"Error: SEPTA API returned status {response.status}"

                data = await response.json()

                if not isinstance(data, list) or len(data) == 0:
                    return f"No upcoming trains from {origin} to {destination}."

                train = data[0]  # Only need next train
                direct = "Yes" if train.get("isdirect") else "No"

                return (
                    f"🚆 **Next Train: {origin.title()} → {destination.title()}**\n"
                    f"**Line:** {train.get('orig_line', 'Unknown')}\n"
                    f"**Train #:** {train.get('orig_train', 'N/A')}\n"
                    f"**Departs:** {train.get('orig_departure_time', 'N/A')}\n"
                    f"**Arrives:** {train.get('orig_arrival_time', 'N/A')}\n"
                    f"**Delay:** {train.get('orig_delay', '0')}\n"
                    f"**Direct:** {direct}"
                )

    except Exception as e:
        return f"Error fetching next train info: {e}"


async def stationList():
    # Just return the list
    return "\n".join(REGIONAL_RAIL_STATIONS)
