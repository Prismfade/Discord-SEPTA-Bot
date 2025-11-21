import discord
import Stations
from discord.ui import View, Select
from Line_Subscription import (
    subscribe_to_line,
    unsubscribe_to_line
)
from dynamic_station import fetch_line_station_map
from Septa_Api import get_line_status

USER_SELECTIONS = {}




from Septa_Api import get_station_arrivals

class StationSelect(Select):
    def __init__(self, stations):
        stations = stations[:25]
        super().__init__(
            placeholder="Select a station",
            options=[discord.SelectOption(label=s) for s in stations]
        )
        self.stations = stations

    async def callback(self, interaction):
        station = self.values[0]
        user_id = interaction.user.id

        # load stored line
        selection = USER_SELECTIONS.get(user_id, {})
        line_name = selection.get("line")

        # save station
        selection["station"] = station
        USER_SELECTIONS[user_id] = selection

        # fetch arrivals
        arrivals_text = await get_station_arrivals(station)

        # detect if there are NO approaching trains
        no_trains = "No upcoming trains for" in arrivals_text

        # fetch line status as well
        from Septa_Api import get_line_status
        line_status = await get_line_status(line_name)

        # build clean Option D output
        if no_trains:
            final_message = (
                f"🛤 **{line_name}** → **{station}**\n\n"
                f"📡 **Station Status:**\n"
                f"No upcoming trains currently approaching **{station}**.\n\n"
                f"📈 **Line Status:**\n"
                f"{line_status}"
            )
        else:
            # normal case: trains exist
            final_message = (
                f"🛤 **{line_name}** → **{station}**\n\n"
                f"{arrivals_text}"
            )

        await interaction.response.send_message(final_message, ephemeral=False)




class StationView(View):
    def __init__(self, stations):
        super().__init__()
        self.add_item(StationSelect(stations))


# class LineSelect(Select):
#     def __init__(self):
#         super().__init__(
#             placeholder="Select a Regional Rail Line",
#             options=[discord.SelectOption(label=l) for l in LINE_OPTIONS]
#         )
class LineSelect(Select):
    def __init__(self, line_map):
        # dropdown of line names
        options = [discord.SelectOption(label=line) for line in line_map.keys()]
        super().__init__(placeholder="Select a Regional Rail Line", options=options)
        self.line_map = line_map

    async def callback(self, interaction):
        line_name = self.values[0]
        stations = self.line_map[line_name]     # get stations from dynamic map

        # save user selected line
        USER_SELECTIONS[interaction.user.id] = {"line": line_name}

        #give the live line status
        status_text = await get_line_status(line_name)

        #make it readable
        station_list = "\n".join(f"- {s}" for s in stations)

        await interaction.response.send_message(
            f"🛤 **{line_name} Line Info**\n\n"
        f"**Status:**\n{status_text}\n\n"
        f"**Stations served:**\n{station_list}",
        view= StationView(stations),
        ephemeral=True
        )

    # async def callback(self, interaction):
    #     line_name = self.values[0]
    #     await interaction.response.send_message(
    #         f"🛤 You selected **{line_name}**.\nNow choose a station:",
    #         view=StationView(line_name),
    #         ephemeral=True
    #     )


class LineView(View):
    #now LineSelect requires line_map
    def __init__(self,line_map):
        super().__init__()
        self.add_item(LineSelect(line_map))

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