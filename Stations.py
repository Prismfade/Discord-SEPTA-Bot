

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

    # If the shortcut exists ,  return the real name
    if key in ALIASES:
        return ALIASES[key]

    # Otherwise return nicely formatted text
    return name.title()