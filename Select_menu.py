import discord
from discord.ui import View, Select
import Stations
# YOUR LINE + STATIONS DICTIONARY HERE
LINE_STATIONS = {
    "Airport Line": [
        "30th Street Station",
        "Suburban Station",
        "Jefferson Station",
        "Temple University",
        "Eastwick",
        "Airport Terminal A",
        "Airport Terminal B",
        "Airport Terminal C-D",
        "Airport Terminal E-F"
    ],

    "Lansdale/Doylestown Line": [
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
        "Temple University",
        "Jefferson Station",
        "Suburban Station",
        "30th Street Station"
    ],

    "Paoli/Thorndale Line": [
        "Thorndale", "Downingtown", "Whitford", "Exton", "Malvern",
        "Paoli", "Daylesford", "Berwyn", "Devon", "Strafford", "Wayne",
        "St. Davids", "Radnor", "Villanova", "Rosemont", "Bryn Mawr",
        "Haverford", "Ardmore", "Wynnewood", "Narberth", "Merion",
        "Overbrook", "30th Street Station", "Suburban Station", "Jefferson Station"
    ]
    }

LINE_OPTIONS = list(LINE_STATIONS.keys())


class StationSelect(Select):
    def __init__(self, line_name):
        stations = LINE_STATIONS[line_name][:25]
        super().__init__(
            placeholder=f"Select a station on {line_name}",
            options=[discord.SelectOption(label=s) for s in stations]
        )
        self.line_name = line_name

    async def callback(self, interaction):
        station = self.values[0]
        await interaction.response.send_message(
            f"🚉 You selected **{station}** on **{self.line_name}**",
            ephemeral=True
        )


class StationView(View):
    def __init__(self, line_name):
        super().__init__()
        self.add_item(StationSelect(line_name))


class LineSelect(Select):
    def __init__(self):
        super().__init__(
            placeholder="Select a Regional Rail Line",
            options=[discord.SelectOption(label=l) for l in LINE_OPTIONS]
        )

    async def callback(self, interaction):
        line_name = self.values[0]
        await interaction.response.send_message(
            f"🛤 You selected **{line_name}**.\nNow choose a station:",
            view=StationView(line_name),
            ephemeral=True
        )


class LineView(View):
    def __init__(self):
        super().__init__()
        self.add_item(LineSelect())
