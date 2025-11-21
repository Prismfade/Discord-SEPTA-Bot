import aiohttp
from Stations import normalize_station

# SEPTA TrainView API (gives real lines + stations)
TRAINVIEW_URL = "https://www3.septa.org/api/TrainView/index.php"


async def fetch_line_station_map():
    # call API
    async with aiohttp.ClientSession() as session:
        async with session.get(TRAINVIEW_URL) as resp:
            data = await resp.json()

    line_map = {}

    # build line -> station list
    for train in data:
        line = train.get("line", "").strip()
        src = normalize_station(train.get("source", "").strip())
        dst = normalize_station(train.get("dest", "").strip())

        if not line:
            continue

        if line not in line_map:
            line_map[line] = set()   # set = avoid duplicates

        if src:
            line_map[line].add(src)
        if dst:
            line_map[line].add(dst)

    # convert to sorted list for dropdown
    return {line: sorted(list(stops)) for line, stops in line_map.items()}
