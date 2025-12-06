import asyncio
import discord
from Stations import normalize_station
from Line_Subscription import (
    get_user_subscriptions,
    subscribe_to_line,
    unsubscribe_to_line,
)
from Septa_Api import (
    get_regional_rail_status,
    get_line_status,
    get_next_train,
    get_station_arrivals,
    build_station_line_map,
)

# simple box format
def box(text: str) -> str:
    return f"```\n{text}\n```"


# hello menu command
async def menu_hello(interaction):
    await interaction.followup.send(box("Hello Septa users!"))


# regional rail status
async def menu_regional_rail_status(interaction):
    await interaction.followup.send("Getting status...")
    msg = await get_regional_rail_status()
    await interaction.followup.send(box(msg))


# show user's subs
async def menu_my_subscriptions(interaction):
    user_id = interaction.user.id
    subs = await get_user_subscriptions(user_id)

    if not subs:
        return await interaction.followup.send("You have no subscriptions yet.")

    text = ", ".join(sorted(subs))
    await interaction.followup.send(f"Your subs:\n**{text}**")


# tell user to use slash dropdown
async def menu_subscribe(interaction):
    await interaction.followup.send("Use `/subscribemenu` to open the subscribe dropdown.")


async def menu_unsubscribe(interaction):
    await interaction.followup.send("Use `/unsubscribemenu` to open the unsubscribe dropdown.")


# station arrivals
async def menu_station(interaction):
    user = interaction.user

    def check(m):
        return m.author.id == user.id and m.channel.id == interaction.channel_id

    # ask + confirm station
    async def get_station():
        while True:
            await interaction.followup.send("Type a station name:")
            try:
                msg = await interaction.client.wait_for("message", timeout=20, check=check)
            except asyncio.TimeoutError:
                return None

            corrected = normalize_station(msg.content)
            if not corrected:
                await interaction.followup.send("I can't find that station.")
                continue

            await interaction.followup.send(f"Did you mean **{corrected}** ? (y/n)")

            try:
                reply = await interaction.client.wait_for("message", timeout=15, check=check)
            except asyncio.TimeoutError:
                return None

            if reply.content.lower().startswith("y"):
                return corrected

            await interaction.followup.send("Okay, try again.")

    station = await get_station()
    if not station:
        return await interaction.followup.send("Stopped.")

    # fetch arrivals
    try:
        result = await get_station_arrivals(station)
    except Exception as e:
        return await interaction.followup.send(f"Error fetching arrivals: {e}")

    # normalize output
    if isinstance(result, (list, dict)):
        try:
            if isinstance(result, list):
                result = "\n".join(str(item) for item in result)
            else:
                result = "\n".join(f"{k}: {v}" for k, v in result.items())
        except:
            result = str(result)

    await interaction.followup.send(box(result))


# check line status
async def menu_line_status(interaction):
    user = interaction.user

    def check(m):
        return m.author.id == user.id and m.channel.id == interaction.channel_id

    # input line name
    async def get_line():
        while True:
            await interaction.followup.send("Type a line name:")
            try:
                msg = await interaction.client.wait_for("message", timeout=20, check=check)
            except asyncio.TimeoutError:
                return None

            corrected = normalize_station(msg.content)
            if not corrected:
                await interaction.followup.send("I cannot identify that line.")
                continue

            await interaction.followup.send(f"Did you mean **{corrected}** ? (y/n)")

            try:
                reply = await interaction.client.wait_for("message", timeout=15, check=check)
            except asyncio.TimeoutError:
                return None

            if reply.content.lower().startswith("y"):
                return corrected

            await interaction.followup.send("Okay, try again.")

    line = await get_line()
    if not line:
        return await interaction.followup.send("Stopped.")

    result = await get_line_status(line)
    await interaction.followup.send(box(result))


# list lines serving a station
async def menu_lines(interaction):
    user = interaction.user

    def check(m):
        return m.author.id == user.id and m.channel.id == interaction.channel_id

    async def get_station():
        while True:
            await interaction.followup.send("Type a station name:")
            try:
                msg = await interaction.client.wait_for("message", timeout=20, check=check)
            except asyncio.TimeoutError:
                return None

            corrected = normalize_station(msg.content)
            if not corrected:
                await interaction.followup.send("I cannot identify that station.")
                continue

            await interaction.followup.send(f"Did you mean **{corrected}** ? (y/n)")

            try:
                reply = await interaction.client.wait_for("message", timeout=15, check=check)
            except asyncio.TimeoutError:
                return None

            if reply.content.lower().startswith("y"):
                return corrected

            await interaction.followup.send("Okay, try again.")

    station = await get_station()
    if not station:
        return await interaction.followup.send("Stopped.")

    mapping = await build_station_line_map()
    found = mapping.get(station)

    if not found:
        return await interaction.followup.send(box(f"No lines found for {station}"))

    text = ", ".join(sorted(found))
    await interaction.followup.send(box(text))


# next train between 2 stations
async def menu_next_train(interaction):
    await interaction.followup.send("Next train search started.")
    user = interaction.user

    def check(m):
        return m.author.id == user.id and m.channel.id == interaction.channel_id

    async def ask(prompt):
        while True:
            await interaction.followup.send(prompt)
            try:
                msg = await interaction.client.wait_for("message", timeout=25, check=check)
            except asyncio.TimeoutError:
                return None

            corrected = normalize_station(msg.content)
            if not corrected:
                await interaction.followup.send("I cannot identify that station.")
                continue

            await interaction.followup.send(f"Did you mean **{corrected}** ? (y/n)")
            try:
                reply = await interaction.client.wait_for("message", timeout=20, check=check)
            except asyncio.TimeoutError:
                return None

            if reply.content.lower().startswith("y"):
                return corrected

            await interaction.followup.send("Okay, try again.")

    origin = await ask("Enter origin station:")
    if not origin:
        return await interaction.followup.send("Stopped.")

    dest = await ask("Enter destination station:")
    if not dest:
        return await interaction.followup.send("Stopped.")

    result = await get_next_train(origin, dest)
    await interaction.followup.send(box(result))


# runs the selected dropdown command
async def run_selected_command(interaction, cmd):

    # make sure followup messages can be used
    if not interaction.response.is_done():
        await interaction.response.defer()

    menu_map = {
        "hello": menu_hello,
        "regional_rail_status": menu_regional_rail_status,
        "my_subscriptions": menu_my_subscriptions,
        "subscribemenu": menu_subscribe,
        "unsubscribemenu": menu_unsubscribe,
        "station": menu_station,
        "check_line_status": menu_line_status,
        "lines": menu_lines,
        "next_train": menu_next_train,
    }

    func = menu_map.get(cmd)
    if func:
        return await func(interaction)

    await interaction.followup.send("Command not found.")


# dropdown menu view
class CommandMenuView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=60)
        self.user_id = user_id

    @discord.ui.select(
        placeholder="Pick a command",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(label="Regional Rail Status", value="regional_rail_status"),
            discord.SelectOption(label="Check Line Status", value="check_line_status"),
            discord.SelectOption(label="Next Train", value="next_train"),
            discord.SelectOption(label="Station Arrivals", value="station"),
            discord.SelectOption(label="Lines for Station", value="lines"),
            discord.SelectOption(label="My Subscriptions", value="my_subscriptions"),
            discord.SelectOption(label="Subscribe", value="subscribemenu"),
            discord.SelectOption(label="Unsubscribe", value="unsubscribemenu"),
            discord.SelectOption(label="Hello", value="hello"),
        ]
    )
    async def menu_select(self, interaction, select):
        value = select.values[0]

        # disable dropdown after pick
        select.disabled = True

        await interaction.response.edit_message(
            content=f"Running **{value}**...",
            view=self
        )

        await run_selected_command(interaction, value)
