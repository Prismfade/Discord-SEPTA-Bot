import discord
from discord.ui import View, Select
from Line_Subscription import subscribe_to_line, unsubscribe_to_line
from Stations import normalize_station
from Septa_Api import get_line_status, get_station_arrivals

USER_SELECTIONS = {}

# ---------------- STATION SELECTION ----------------
class StationSelect(Select):
    def __init__(self, stations):
        stations = stations[:25]
        super().__init__(placeholder="Select a station", options=[discord.SelectOption(label=s) for s in stations])
        self.stations = stations

    async def callback(self, interaction):
        station = self.values[0]
        user_id = interaction.user.id

        selection = USER_SELECTIONS.get(user_id, {})
        line_name = selection.get("line")
        selection["station"] = station
        USER_SELECTIONS[user_id] = selection

        arrivals_text = await get_station_arrivals(station)
        line_status = await get_line_status(line_name)
        final_message = f"🛤 **{line_name}** → **{station}**\n\n{arrivals_text}\n\n📈 **Line Status:**\n{line_status}"
        await interaction.response.send_message(final_message, ephemeral=False)

class StationView(View):
    def __init__(self, stations):
        super().__init__()
        self.add_item(StationSelect(stations))

# ---------------- LINE SELECTION ----------------
class LineSelect(Select):
    def __init__(self, line_map):
        options = [discord.SelectOption(label=line) for line in line_map.keys()]
        super().__init__(placeholder="Select a Regional Rail Line", options=options)
        self.line_map = line_map

    async def callback(self, interaction):
        line_name = self.values[0]
        stations = self.line_map[line_name]
        USER_SELECTIONS[interaction.user.id] = {"line": line_name}
        status_text = await get_line_status(line_name)
        station_list = "\n".join(f"- {s}" for s in stations)
        await interaction.response.send_message(
            f"🛤 **{line_name} Line Info**\n\n**Status:**\n{status_text}\n\n**Stations served:**\n{station_list}",
            view=StationView(stations),
            ephemeral=True
        )

class LineView(View):
    def __init__(self, line_map):
        super().__init__()
        self.add_item(LineSelect(line_map))

# ---------------- SUBSCRIBE / UNSUBSCRIBE ----------------
class SubscribeLineSelect(Select):
    def __init__(self, line_names):
        super().__init__(placeholder="Select a line to subscribe", options=[discord.SelectOption(label=l) for l in line_names])

    async def callback(self, interaction):
        user_id = interaction.user.id
        line_name = self.values[0]
        result = await subscribe_to_line(user_id, line_name)
        await interaction.response.send_message(f"✅ {result}", ephemeral=True)

class SubscribeLineView(View):
    def __init__(self, line_names):
        super().__init__()
        self.add_item(SubscribeLineSelect(line_names))

class UnsubscribeLineSelect(Select):
    def __init__(self, user_subs):
        super().__init__(placeholder="Select a line to unsubscribe", options=[discord.SelectOption(label=l) for l in user_subs])

    async def callback(self, interaction):
        user_id = interaction.user.id
        line_name = self.values[0]
        result = await unsubscribe_to_line(user_id, line_name)
        await interaction.response.send_message(f"❌ {result}", ephemeral=True)

class UnsubscribeLineView(View):
    def __init__(self, user_subs):
        super().__init__()
        self.add_item(UnsubscribeLineSelect(user_subs))