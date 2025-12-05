
import difflib

#All the possible stations
REGIONAL_RAIL_STATIONS = [
    "30th Street Station",
    "Suburban Station",
    "Jefferson Station",
    "Temple University",

    "Eastwick",
    "Airport Terminal A",
    "Airport Terminal B",
    "Airport Terminal C-D",
    "Airport Terminal E-F",

    "Chestnut Hill East",
    "Gravers",
    "Wyndmoor",
    "Mount Airy",
    "Sedgwick",
    "Stenton",
    "Washington Lane",
    "Wayne Junction",

    "Chestnut Hill West",
    "Highland",
    "St. Martins",
    "Allen Lane",
    "Carpenter",
    "Upsal",
    "Tulpehocken",
    "Chelten Avenue",
    "Queen Lane",
    "North Philadelphia",
    "North Broad",

    "Cynwyd",
    "Bala",
    "Wynnefield Avenue",

    "Fox Chase",
    "Ryers",
    "Cheltenham",
    "Lawndale",
    "Olney",

    "Doylestown",
    "Delaware Valley University",
    "New Britain",
    "Chalfont",
    "Colmar",
    "Fortuna",
    "Hatfield",
    "Lansdale",
    "Pennbrook",
    "North Wales",
    "Gwynedd Valley",
    "Penllyn",
    "Ambler",
    "Fort Washington",
    "Oreland",
    "Glenside",
    "Jenkintown-Wyncote",

    "Elm Street",
    "Norristown Transportation Center",
    "Main Street",
    "Conshohocken",
    "Spring Mill",
    "Miquon",
    "Ivy Ridge",
    "Manayunk",
    "East Falls",
    "Allegheny",

    "Wawa",
    "Elwyn",
    "Media",
    "Moylan-Rose Valley",
    "Wallingford",
    "Swarthmore",
    "Morton",
    "Prospect Park",
    "Norwood",
    "Glenolden",
    "Folcroft",
    "Sharon Hill",
    "Curtis Park",
    "Darby",

    "Thorndale",
    "Downingtown",
    "Whitford",
    "Exton",
    "Malvern",
    "Paoli",
    "Daylesford",
    "Berwyn",
    "Devon",
    "Strafford",
    "Wayne",
    "St. Davids",
    "Radnor",
    "Villanova",
    "Rosemont",
    "Bryn Mawr",
    "Haverford",
    "Ardmore",
    "Wynnewood",
    "Narberth",
    "Merion",
    "Overbrook",

    "Trenton",
    "Levittown",
    "Bristol",
    "Croydon",
    "Eddington",
    "Cornwells Heights",
    "Torresdale",
    "Holmesburg Junction",
    "Tacony",
    "Bridesburg",

    "Warminster",
    "Hatboro",
    "Willow Grove",
    "Crestmont",
    "Roslyn",
    "Ardsley",

    "West Trenton",
    "Yardley",
    "Woodbourne",
    "Langhorne",
    "Neshaminy Falls",
    "Trevose",
    "Somerton",
    "Forest Hills",
    "Philmont",
    "Bethayres",
    "Meadowbrook",
    "Rydal",
    "Noble",

    "Newark",
    "Churchmans Crossing",
    "Wilmington",
    "Claymont",
    "Marcus Hook",
    "Highland Avenue",
    "Chester",
    "Eddystone",
    "Crum Lynne",
    "Ridley Park"
]

#use Aliases for typo so user don't need to input everything
ALIASES = {

    #Some that my friend uses
    "fox":  "Fox Chase",
    "fx": "Fox Chase",
    "fox ch": "Fox Chase",

    # 30th Street
    "30th": "30th Street Station",
    "30th st": "30th Street Station",
    "30th street": "30th Street Station",
    "thirty street": "30th Street Station",
    "thirtieth street": "30th Street Station",

    # Temple
    "temple": "Temple University",
    "temple u": "Temple University",
    "temple univ": "Temple University",
    "tu": "Temple University",

    # Suburban & Jefferson
    "suburban": "Suburban Station",
    "jefferson": "Jefferson Station",

    # Norristown / NTC / Elm
    "norristown": "Norristown Transportation Center",
    "noristown": "Norristown Transportation Center",   # common typo
    "ntc": "Norristown Transportation Center",
    "norristown tc": "Norristown Transportation Center",
    "elm": "Elm Street",
    "elm st": "Elm Street",

    # Glenside
    "glenside": "Glenside",
    "glensaid": "Glenside",
    "glen side": "Glenside",

    # Airport Terminals
    "airport": "Airport Terminal A",
    "airport a": "Airport Terminal A",
    "terminal a": "Airport Terminal A",
    "terminal b": "Airport Terminal B",
    "terminal c": "Airport Terminal C-D",
    "terminal d": "Airport Terminal C-D",
    "terminal e": "Airport Terminal E-F",
    "terminal f": "Airport Terminal E-F",

    # Paoli Line short names
    "ardmore": "Ardmore",
    "villanova": "Villanova",
    "radnor": "Radnor",
    "wayne": "Wayne",

    # Trenton Line
    "trenton": "Trenton",
    "cornwells": "Cornwells Heights",

    # Wilmington/Newark
    "wilmington": "Wilmington",
    "newark": "Newark",

    # Chestnut Hill lines
    "chestnut hill east": "Chestnut Hill East",
    "chestnut hill west": "Chestnut Hill West",
    "ch east": "Chestnut Hill East",
    "ch west": "Chestnut Hill West",
}

def normalize_station(name: str):
    key = name.lower().strip()

    # Check alias shortcuts
    if key in ALIASES:
        return ALIASES[key]

    # Perfect match
    for station in REGIONAL_RAIL_STATIONS:
        if key == station.lower():
            return station

    # Fuzzy guess

    suggestion = suggest_station(name)
    if suggestion:
        return suggestion

    # Fallback
    return name.title()




def suggest_station(user_input):
    user_input = user_input.lower().strip()

    #all the possible ways to fix the typo

    if user_input.startswith("tem"):
        return "Temple University"

    if user_input.startswith("f") and "h" not in user_input:
        return "Fox Chase"

    if user_input.startswith("sub"):
        return "Suburban Station"

    if user_input.startswith("jef"):
        return "Jefferson Station"

    if user_input.startswith("nor") and "tc" in user_input:
        return "Norristown Transportation Center"



    # First get a few possible close matches
    matches = difflib.get_close_matches(
        user_input,
        [s.lower() for s in REGIONAL_RAIL_STATIONS],
        n=3,
        cutoff=0.4
    )

    if not matches:
        return None

    # Convert back to original capitalization
    matches = [
        station for station in REGIONAL_RAIL_STATIONS
        if station.lower() in matches
    ]

    # Prefer matches that start with the same letter
    same_letter = [
        s for s in matches
        if s[0].lower() == user_input[0].lower()
    ]
    if same_letter:
        return same_letter[0]

    # Otherwise return the best fuzzy match
    return matches[0]

REGIONAL_RAIL_LINES = [
    "Lansdale/Doylestown",
    "Paoli/Thorndale",
    "Warminster",
    "West Trenton",
    "Airport",
    "Media/Wawa",
    "Fox Chase",
    "Chestnut Hill East",
    "Chestnut Hill West",
    "Cynwyd",
    "Manayunk/Norristown",
    "Trenton",
    "Wilmington/Newark",
]

def normalize_line(name: str) -> str:
    key = name.lower().strip()

    if key.startswith("lans"):
        return "Lansdale/Doylestown"
    if key.startswith("pao") or key.startswith("paol"):
        return "Paoli/Thorndale"
    if key.startswith("war"):
        return "Warminster"
    if key.startswith("west"):
        return "West Trenton"
    if key.startswith("trent"):
        return "Trenton"
    if key.startswith("wilm") or key.startswith("newa"):
        return "Wilmington/Newark"
    if key.startswith("air"):
        return "Airport"
    if key.startswith("media") or key.startswith("wawa"):
        return "Media/Wawa"
    if key.startswith("mana") or key.startswith("norristown"):
        return "Manayunk/Norristown"
    if key.startswith("fox"):
        return "Fox Chase"
    if key.startswith("chestnut hill e"):
        return "Chestnut Hill East"
    if key.startswith("chestnut hill w"):
        return "Chestnut Hill West"
    if key.startswith("cyn") or key.startswith("cynw"):
        return "Cynwyd"

    # exact match first
    for line in REGIONAL_RAIL_LINES:
        if key == line.lower():
            return line

    match = difflib.get_close_matches(
        key,
        [l.lower() for l in REGIONAL_RAIL_LINES],
        n=1,
        cutoff=0.7
    )
    if match:
        return next(l for l in REGIONAL_RAIL_LINES if l.lower() == match[0])

    return name.title()