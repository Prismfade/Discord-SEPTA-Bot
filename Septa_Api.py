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

                # get raw delay text from API (could be number or words)
                raw_delay = (train.get("orig_delay") or "").strip()
                raw_delay_lower = raw_delay.lower()

                # check if delay is a number (ex: "5", "10", "-2")
                if raw_delay.lstrip("+-").isdigit():
                    delay = int(raw_delay)
                else:
                    delay = 0   # if it's words like "On time" just treat as 0

                # build the status message
                if "cancel" in raw_delay_lower:
                    status_str = "Cancelled ❌"
                elif "suspend" in raw_delay_lower:
                    status_str = "Suspended 🚫"
                elif "terminate" in raw_delay_lower:
                    status_str = "Service terminated ❌"
                elif "depart" in raw_delay_lower:
                    status_str = "Departed 🚆"
                elif "on time" in raw_delay_lower or delay == 0:
                    status_str = "On time ✅"
                elif delay <= 5:
                    status_str = f"{delay} min late ⚠️"
                else:
                    status_str = f"{delay} min late ⛔"

                return (
                    f"🚆 **Next Train: {origin.title()} → {destination.title()}**\n"
                    f"**Line:** {train.get('orig_line', 'Unknown')}\n"
                    f"**Train #:** {train.get('orig_train', 'N/A')}\n"
                    f"**Departs:** {train.get('orig_departure_time', 'N/A')}\n"
                    f"**Arrives:** {train.get('orig_arrival_time', 'N/A')}\n"
                    f"**Status:** {status_str}\n"
                    f"**Direct:** {direct}"
                )

    except Exception as e:
        return f"Error fetching next train info: {e}"


async def stationList():
    # Just return the list
    return "\n".join(REGIONAL_RAIL_STATIONS)

#mapping stations to the train lines
async  def build_station_line_map():
    url = "https://www3.septa.org/api/TrainView/index.php"
    station_to_lines = {}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()

                for train in data:
                    line = train.get("line","").strip()
                    next_stop = train.get("nextstop","").strip()

                    if not line or not next_stop:
                        continue

                    #capitalization
                    next_stop = next_stop.title()
                    line = line.title()

                    #mapping it
                    station_to_lines.setdefault(next_stop,set()).add(line)

            return station_to_lines

    except Exception as e:
        return {}

async def get_station_arrivals(station_name):

    # Convert whatever the user typed into a proper station name
    station = normalize_station(station_name)
    url = "https://www3.septa.org/api/TrainView/index.php"

    arrivals = []

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()

        # Helper: TrainView sometimes uses different spellings for stations.
        # This converts all versions into one consistent name.
        def normalize_nextstop(stop):
            stop = stop.lower().strip()

            # Temple has multiple formats in TrainView
            if stop in ["temple u", "temple university", "temple"]:
                return "Temple University"

            # All other stations: title-case them
            return stop.title()

        # Loop through every train and see if it is coming to our station
        for train in data:
            next_stop_raw = train.get("nextstop", "").strip()
            if not next_stop_raw:
                continue

            next_stop = normalize_nextstop(next_stop_raw)

            if next_stop == station:
                arrivals.append(train)

        # No trains? Tell the user.
        if not arrivals:
            return f"No upcoming trains for {station}"

        # Start building the message
        message_lines = [f"Incoming trains for **{station}**:\n"]

        # Sort trains by earliest arrival time
        arrivals_sorted = sorted(
            arrivals,
            key=lambda t: int(t.get("due", "999") or 999)
        )

        for train in arrivals_sorted:
            line = train.get("line", "Unknown Line").title()
            train_no = train.get("trainno", "N/A")
            due = train.get("due", "N/A")
            delay = int(train.get("late", 0))



            # Calculate the actual arrival time (right now + due minutes)
            try:
                due_minutes = int(due)
                from datetime import datetime, timedelta
                arrival_time = datetime.now() + timedelta(minutes=due_minutes)
                arrival_str = arrival_time.strftime("%I:%M %p").lstrip("0")
            except:
                arrival_str = "N/A"



            # Determine if it's late or on time
            if delay == 0:
                status = "On time ✅"
            elif delay <= 5:
                status = f"{delay} min late ⚠️"
            else:
                being_cancel = "Canceled 😡"
                if delay >= 999:
                    status = f"{being_cancel}"
                else :
                    status = f"{delay} min late ⛔"


            # Add info about this train to the message
            message_lines.append(
                f"🚆 **{line}**  Train **{train_no}**\n"
                f"Arriving in **{due} min** (at **{arrival_str}**)\n"
                f"Status: {status}\n"
            )

        # Return everything as a single message
        return "\n".join(message_lines)

    except Exception as e:
        return f"Error fetching arrivals: {e}"