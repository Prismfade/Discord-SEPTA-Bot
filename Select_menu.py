import discord
import Stations
from discord.ui import View, Select
from Line_Subscription import (
    subscribe_to_line,
    unsubscribe_to_line
)

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

async def build_subscribe_line_view():
    from Septa_Api import get_unique_regional_rail_lines
    line_names = await get_unique_regional_rail_lines()
    if not line_names:
        line_names = ["No lines available"]

    # Inner Select class created with dynamic options
    class SubscribeLineSelect(Select):
        def __init__(self):
            super().__init__(
                placeholder="Select a Regional Rail Line",
                options=[discord.SelectOption(label=line) for line in line_names]
            )

        async def callback(self, interaction):
            user_id = interaction.user.id
            line_name = self.values[0]
            result = await subscribe_to_line(user_id, line_name)
            await interaction.response.send_message(
                f"✅ {result}\nChange your mind? Use `!unsubscribe`.", ephemeral=True
            )

    class SubscribeLineView(View):
        def __init__(self):
            super().__init__()
            self.add_item(SubscribeLineSelect())

    return SubscribeLineView()

async def build_unsubscribe_view(user_subs):
    if not user_subs:
        user_subs = ["No subscriptions"]

    class UserLineSelect(Select):
        def __init__(self):
            options = [discord.SelectOption(label=line) for line in user_subs]
            super().__init__(placeholder="Select a line to unsubscribe from", options=options)

        async def callback(self, interaction):
            line_name = self.values[0]
            result = await unsubscribe_to_line(interaction.user.id, line_name)
            await interaction.response.send_message(
                f"❌ {result}\nChange your mind? Use `!subscribe`.", ephemeral=True
            )

    class UserLineView(View):
        def __init__(self):
            super().__init__()
            self.add_item(UserLineSelect())

    return UserLineView()