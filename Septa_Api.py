import aiohttp
from datetime import datetime,timedelta

from Stations import REGIONAL_RAIL_STATIONS, normalize_station
# STATIONS_CACHE = []  -> might not need it no more? since i made the whole listing myself
# Fetch SEPTA Regional Rail Status

def clean_time(raw):
    try:
        dt = datetime.strptime(raw, "%Y-%m-%d %H:%M:%S.%f")
        return dt.strftime("%I:%M %p").lstrip("0"), dt
    except:
        return "N/A", None

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

                trains = []
                for train in data[:10]:
                    line = train.get("line", "Unknown Line")
                    train_id = train.get("trainno", "Unknown Train")
                    delay = train.get("late", 0)
                    if int(delay) >= 500:
                        emoji = "❌"
                        status = "Canceled"
                    else:
                        # Choose emoji based on delay
                        emoji = "🟢" if delay == 0 else "🛑"
                        status = "on time" if delay == 0 else f"{delay} min late"


                        # Format with emoji FIRST
                    trains.append(f"{emoji} 🚆 {line} Train {train_id}: {status}")

                return "\n".join(trains)

    except Exception as e:
        return f"Error fetching SEPTA data: {e}"

def get_direction_from_dest(dest: str) -> str:
    """
    Determine whether the train is Inbound or Outbound using the destination.
    Inbound  = heading toward Center City stations.
    Outbound = heading away from Center City.
    """

    if not dest:
        return "➡️ Outbound"  # default if no destination provided

    d = dest.lower().strip()

    # All trains heading INTO Center City should be labeled inbound
    inbound_keywords = [
        "jefferson",        # Jefferson Station
        "suburban",         # Suburban Station
        "30th",             # 30th Street Station
        "temple",           # Temple University
        "university city",  # University City / Penn Medicine
        "center",           # "Center City"
    ]

    # If destination matches any inbound station -> inbound
    if any(k in d for k in inbound_keywords):
        return "⬅️ Inbound"

    # Everything else -> outbound
    return "➡️ Outbound"


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

                delayed = []
                for train in matching_trains:
                    line = train.get("line", "Unknown Line")
                    train_id = train.get("trainno", "Unknown Train")
                    delay = train.get("late", 0)
                    dest = train.get("dest", "Unknown destination")

                    direction = get_direction_from_dest(dest)

                    # Existing status logic
                    if delay == 0:
                        status = "On time ✅"
                    elif delay <= 5:
                        status = f"{delay} min late ⚠️"
                    else:
                        being_cancel = "Canceled 😡"
                        if delay >= 999:
                            status = f"{being_cancel}"
                        else:
                            status = f"{delay} min late ⛔"

                    delayed.append(
                        f"{direction} 🚆 {line} Train {train_id} → {dest} : {status}"
                    )

                if not delayed:
                    return f"Line is active and all trains are on time. ✅"

                legend = (
                "\n\n**Legend:**\n"
                "⬅️ **Inbound** = Train heading *toward Center City* (Jefferson, Suburban, 30th St, Temple)\n"
                "➡️ **Outbound** = Train heading *away from Center City*\n"
                )

                return "\n".join(delayed[:10]) + legend

    except Exception as e:
        return f"Error fetching SEPTA data: {e}"
    
# Fetch SEPTA Line by Name (All trains)
async def get_unique_regional_rail_lines():
    url = "https://www3.septa.org/api/TrainView/index.php"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return []
                data = await response.json()
                lines = {train.get("line", "").title() for train in data if train.get("line")}
                return sorted(lines)
    except Exception as e:
        return []


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

    unsupported_station ={
        "norristown",
        "norristown tc",
        "norristown transportation center",
        "norristown transit center",
        "ntc",
    }

    if station.lower() in unsupported_station:

        return (
            "⚠️ **Norristown does not provide live arrival data in SEPTA’s API.**\n"
            "SEPTA does not publish arrivals for this stop.\n\n"
            "Nearby stations with live arrival data:\n"
            "• **Manayunk**\n"
            "• **Miquon**\n"
            "• **Conshohocken**"
        )

    url = "https://www3.septa.org/api/TrainView/index.php"
    url2 = f"https://www3.septa.org/api/Arrivals/index.php?station={station}"
    arrivals = []
    

    try:
        # First fetch: TrainView
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()

         # Second fetch: Arrivals API
            async with session.get(url2) as response2:
                arrival_data = await response2.json()
            actual_key = list(arrival_data.keys())[0]
            direction_groups = arrival_data[actual_key]
            arrival_list =[]
            for group in direction_groups:
                for direction_name, trains in group.items():
                    #trains a list
                    arrival_list.extend(trains)

            arrivals_by_trainno = { str(item["train_id"]): item for item in arrival_list }
            

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
            if not next_stop_raw or next_stop_raw.lower() == "null":
                continue

            next_stop = normalize_nextstop(next_stop_raw)  # clean API value
            station_norm = station.lower()

            # Fuzzy matching: station contains API name OR API name contains station
            if station_norm in next_stop.lower() or next_stop.lower() in station_norm:
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
            arr_info = arrivals_by_trainno.get(str(train_no))
            raw_arr = arr_info.get("sched_time") if arr_info else None
            sched_arrival_str, sched_arrival_dt = clean_time(raw_arr)
            track = arr_info.get("track", "N/A") if arr_info else "N/A"
            official_status = arr_info.get("status", "N/A") if arr_info else "N/A"


            #always add 1 to departrue cz ppl r dealing with getting on n off
            if sched_arrival_dt:
    
                depart_dt = sched_arrival_dt + timedelta(minutes=1)
                sched_depart_str = depart_dt.strftime("%I:%M %p").lstrip("0")
            else:
                sched_depart_str = "N/A"

            #compute ETA
            if sched_arrival_dt:
                now = datetime.now()
                eta_delta = sched_arrival_dt -now
                eta_minutes = max(int(eta_delta.total_seconds() // 60), 0)
            else:
                eta_minutes = 999

            if eta_minutes >= 500:
                eta_display = "❌ Canceled"
            else:
                eta_display = f"{eta_minutes} min"

            # Calculate the actual arrival time (right now + due minutes)
            # try:
            #     due_minutes = int(due)
            #     from datetime import datetime, timedelta
            #     # arrival_time = datetime.now() + timedelta(minutes=due_minutes)
            #     # arrival_str = arrival_time.strftime("%I:%M %p").lstrip("0")
            # except:
            #     arrival_str = "N/A"



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
                f"Scheduled arrival: **{sched_arrival_str}**\n"
                f"Scheduled departure: **{sched_depart_str}**\n"
                f"Track: **{track}**\n"
                f"ETA: Arriving in **{eta_display}**(at **{sched_arrival_str}**)\n"
                f"Status: {official_status}\n"

            )

        # Return everything as a single message
        return "\n".join(message_lines)

    except Exception as e:
        return f"Error fetching arrivals: {e}"