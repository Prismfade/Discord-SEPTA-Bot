import os
import random
import asyncio
import logging
from typing import List

import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

from Select_menu import (
    LineView,
    build_subscribe_line_view,
    build_unsubscribe_view,
)
from dynamic_station import fetch_line_station_map

from Line_Subscription import (
    subscribe_to_line,
    unsubscribe_to_line,
    get_user_subscriptions,
    notify_line,
    user_line_subscriptions,
)
from Stations import normalize_station, REGIONAL_RAIL_STATIONS

from Septa_Api import (
    get_regional_rail_status,
    get_line_status,
    get_next_train,
    stationList,
    get_station_arrivals,
    get_unique_regional_rail_lines,  # ✅ needed for /check line status error handling
)

from station_alerts import StationAlerts  # alert/background cog

#box_text format

def box(text: str)-> str:
    return f"```\n{text}\n```"

COMMAND_LIST = []


def register(cmd_name: str):
    COMMAND_LIST.append(cmd_name)


register("/help")
register("/regional_rail_status")
register("/check_line_status")
register("/next_train")
register("/station")
register("/menu")
register("/lines")
register("/hello")
register("/my_subscriptions")
register("/subscribemenu")
register("/unsubscribemenu")


# ---------------------------
# ENV + TOKEN
# ---------------------------
load_dotenv()
token = os.getenv("DISCORD_TOKEN")

if not token:
    print("Error: DISCORD_TOKEN not found. Check your .env file.")
    exit()

# ---------------------------
# LOGGING
# ---------------------------
handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")

# ---------------------------
# INTENTS
# ---------------------------
intents = discord.Intents.default()
intents.message_content = True
intents.members = True


# ---------------------------
# Bot class
# ---------------------------
class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None,
        )

    async def setup_hook(self):
        # Load the StationAlerts cog so background alerts start running
        await self.add_cog(StationAlerts(self))


bot = MyBot()


# ---------------------------
# Events
# ---------------------------
@bot.event
async def on_ready():
    await bot.tree.sync()
    print("Global commands synced!")
    print("Bot is online!")
    print(f"Logged in as {bot.user.name} - {bot.user.id}")
    print("------")

    channel_id = 1437230785072463882
    channel = bot.get_channel(channel_id)

    if channel:
        await channel.send(
            "**👋 Hey! I'm the SEPTA Status Bot.**\n"
            "I can check train delays, next arrivals, station information, and send outage alerts.\n"
            "Type **/help** to see what I can do!\n"
        )


# ---------------------------
# Slash commands
# ---------------------------
@bot.tree.command(name="hello", description="Test slash command")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("Hello Septa users!")


@bot.tree.command(
    name="regional_rail_status", description="Shows live delays on all Regional Rail trains."
)
async def regional_rail_status(interaction: discord.Interaction):
    await interaction.response.send_message(box("Fetching live status…"))
    status_message = await get_regional_rail_status()
    await interaction.followup.send(box(status_message))


@bot.tree.command(name="station", description="Get arrival times for a station")
@app_commands.describe(name="Type a Regional Rail Station")
async def station(interaction: discord.Interaction, name: str):
    station_norm = normalize_station(name)
    result = await get_station_arrivals(station_norm)
    await interaction.response.send_message(box(result))


@bot.tree.command(
    name="check_line_status", description="Lets you check any specific train line."
)
@app_commands.describe(name="Type a Regional Rail line")
async def check_line_status_slash(interaction: discord.Interaction, name: str):
    await interaction.response.send_message(box(
        "Which train line would you like to check? (e.g. Paoli, Trenton, Lansdale)"
    ))

    def check(m: discord.Message):
        return (
            m.author.id == interaction.user.id
            and m.channel.id == interaction.channel.id
        )

    try:
        user_msg = await bot.wait_for("message", check=check, timeout=20)
        line_name = user_msg.content.strip()
        await interaction.followup.send(f"Fetching **{line_name.title()} Line** status…")

        status_message = await get_line_status(line_name)
        await interaction.followup.send(box(status_message))
    except Exception:
        await interaction.followup.send(box(
            "⏰ You didn’t reply in time or an error occurred. Try again."
        ))


@bot.tree.command(
    name="next_train", description="Shows the next train between two stations."
)
@app_commands.describe(
    origin="Origin Regional Rail station",
    destination="Destination Regional Rail station",
)
async def next_train_slash(
    interaction: discord.Interaction,
    origin: str,
    destination: str,
):
    origin_norm = normalize_station(origin)
    dest_norm = normalize_station(destination)

    invalid_bits = []

    if origin_norm not in REGIONAL_RAIL_STATIONS:
        invalid_bits.append(f"origin station **{origin}**")

    if dest_norm not in REGIONAL_RAIL_STATIONS:
        invalid_bits.append(f"destination station **{destination}**")

    if invalid_bits:
        msg = (
            "⚠️ I couldn't find "
            + " and ".join(invalid_bits)
            + " in the Regional Rail station list.\n"
            "Please check the spelling, or try `/station` to look up a station."
        )
        await interaction.response.send_message(msg)
        return

    await interaction.response.send_message(box(
        f"Fetching the next train from **{origin_norm} → {dest_norm}**…"
    ))

    try:
        status_message = await get_next_train(origin_norm, dest_norm)
        await interaction.followup.send(box(status_message))
    except Exception:
        logging.exception(
            "Error in /next_train origin=%s dest=%s",
            origin_norm,
            dest_norm,
        )
        await interaction.followup.send(
            "⚠️ Sorry, something went wrong while fetching that trip.\n"
            "Please double-check your station names or try again in a minute."
        )


@bot.tree.command(
    name="lines", description="Shows what lines serve a Regional Rail station."
)
async def lines_slash(interaction: discord.Interaction):
    await interaction.response.send_message(box(
        "Which station do you want to check? (e.g. Temple University, Suburban Station)"
    ))

    def check(m: discord.Message):
        return (
            m.author.id == interaction.user.id
            and m.channel.id == interaction.channel.id
        )

    try:
        user_msg = await bot.wait_for("message", check=check, timeout=20)
        station_raw = user_msg.content.strip()
        station_norm = normalize_station(station_raw)

        from Septa_Api import build_station_line_map

        station_map = await build_station_line_map()
        lines_for_station = station_map.get(station_norm)

        if not lines_for_station:
            await interaction.followup.send(box(
                f"⚠️ I couldn't find any lines serving **{station_raw}**.\n"
                "Please check the spelling, or try `/station` to look up arrivals."
            ))
            return

        lines_list = ", ".join(sorted(lines_for_station))
        await interaction.followup.send(box(
            f"🚆 **{station_norm}** is served by these lines:\n{lines_list}"
        ))

    except asyncio.TimeoutError:
        await interaction.followup.send(
            "⏰ You didn’t reply in time. Try `/lines` again when you’re ready."
        )
    except Exception:
        logging.exception("Error in /lines command")
        await interaction.followup.send(
            "⚠️ Something went wrong while looking up that station. Please try again."
        )


@bot.tree.command(name="sync", description="Force global sync")
async def sync_slash(interaction: discord.Interaction):
    await bot.tree.sync()
    await interaction.response.send_message(box("Global commands synced!"))


# ---------- Slash subscription commands (simple text) ---------- #

@bot.tree.command(
    name="subscribe_line",
    description="Subscribe to outage alerts for a Regional Rail line.",
)
@app_commands.describe(line_name="Name of the Regional Rail line (e.g. Lansdale/Doylestown)")
async def subscribe_line_slash(interaction: discord.Interaction, line_name: str):
    user_id = interaction.user.id
    await subscribe_to_line(user_id, line_name)
    await interaction.response.send_message(
        f"✅ You are now subscribed to alerts for **{line_name}**.",
        ephemeral=True,
    )


@bot.tree.command(
    name="unsubscribe_line",
    description="Unsubscribe from outage alerts for a Regional Rail line.",
)
@app_commands.describe(line_name="Name of the Regional Rail line to unsubscribe.")
async def unsubscribe_line_slash(interaction: discord.Interaction, line_name: str):
    user_id = interaction.user.id
    await unsubscribe_to_line(user_id, line_name)
    await interaction.response.send_message(
        f"✅ You are unsubscribed from alerts for **{line_name}**.",
        ephemeral=True,
    )


@bot.tree.command(
    name="my_subscriptions",
    description="Show which Regional Rail lines you are subscribed to.",
)
async def my_subscriptions_slash(interaction: discord.Interaction):
    user_id = interaction.user.id
    subs = await get_user_subscriptions(user_id)
    if not subs:
        msg = "You are not subscribed to any lines yet. Use `/subscribe_line` or `/subscribemenu` to get started."
    else:
        lines = ", ".join(sorted(subs))
        msg = f"You're subscribed to alerts for:\n**{lines}**"
    await interaction.response.send_message(msg, ephemeral=True)

@bot.tree.command(name="help", description="Show all available commands for the SEPTA bot.")
async def help_slash(interaction: discord.Interaction):
    help_text = """Available Commands:

/regional_rail_status - Live delays for all Regional Rail trains.
/check_line_status - Check any specific train line.
/next_train - Next train between two stations.
/station - Arrivals for a station.
/lines - What lines serve a station.

/my_subscriptions - See your subscriptions.
/subscribemenu - Subscribe to outage alerts.
/unsubscribemenu - Unsubscribe from alerts.

!subscribe - Prefix subscribe.
!unsubscribe - Prefix unsubscribe.
!mysubscriptions - Prefix list.
"""

    await interaction.response.send_message(f"```\n{help_text}\n```")

# Autocomplete for /station
@station.autocomplete("name")
async def station_autocomplete(
    interaction: discord.Interaction, current: str
) -> List[app_commands.Choice[str]]:
    stations = REGIONAL_RAIL_STATIONS
    matches = [s for s in stations if current.lower() in s.lower()]
    return [app_commands.Choice(name=s, value=s) for s in matches[:25]]


# ---------------------------
# Subscription dropdown views
# ---------------------------
class SubscribeLineView(discord.ui.View):
    """
    Dropdown menu for subscribing to a Regional Rail line.
    """

    def __init__(self, lines: List[str], user_id: int, *, timeout: float | None = 60):
        super().__init__(timeout=timeout)
        self.user_id = user_id
        self.select.options = [
            discord.SelectOption(label=line, value=line) for line in lines[:25]
        ]

    @discord.ui.select(
        placeholder="Select a Regional Rail line to subscribe to...",
        min_values=1,
        max_values=1,
        options=[],
    )
    async def select(
        self,
        interaction: discord.Interaction,
        select: discord.ui.Select,
    ):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "This menu isn’t for you. Please run your own `!subscribemenu` or `/subscribemenu`.",
                ephemeral=True,
            )
            return

        line_name = select.values[0]
        await subscribe_to_line(self.user_id, line_name)

        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(
            content=f"✅ You are now subscribed to outage alerts for **{line_name}**.",
            view=self,
        )


class UnsubscribeLineView(discord.ui.View):
    """
    Dropdown menu for unsubscribing from a Regional Rail line.
    """

    def __init__(self, lines: List[str], user_id: int, *, timeout: float | None = 60):
        super().__init__(timeout=timeout)
        self.user_id = user_id
        self.select.options = [
            discord.SelectOption(label=line, value=line) for line in lines[:25]
        ]

    @discord.ui.select(
        placeholder="Select a Regional Rail line to unsubscribe from...",
        min_values=1,
        max_values=1,
        options=[],
    )
    async def select(
        self,
        interaction: discord.Interaction,
        select: discord.ui.Select,
    ):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "This menu isn’t for you. Please run your own `!unsubscribemenu` or `/unsubscribemenu`.",
                ephemeral=True,
            )
            return

        line_name = select.values[0]
        await unsubscribe_to_line(self.user_id, line_name)

        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(
            content=f"✅ You are unsubscribed from outage alerts for **{line_name}**.",
            view=self,
        )


# ---------------------------
# on_message: prefix commands
# ---------------------------
@bot.event
async def on_message(message: discord.Message):
    current_status = "Bad , very heavy load"
    if message.author == bot.user:
        return

    content = message.content.lower()

    # if "/regional rail status" in content:
    #     await message.channel.send("Fetching live SEPTA Regional Rail status… ")
    #     status_message = await get_regional_rail_status()
    #     await message.channel.send(box(status_message))

    # elif "/check line status" in content:
    #     await message.channel.send(
    #         "Which train line would you like to check? (e.g. Paoli, Trenton, Lansdale)"
    #     )

    #     def check(m: discord.Message):
    #         return m.author == message.author and m.channel == message.channel

    #     try:
    #         user_msg = await bot.wait_for("message", check=check, timeout=20)
    #         line_name = user_msg.content.strip()
    #         await message.channel.send(
    #             f"Fetching {line_name.title()} Line status… "
    #         )

    #         status_message = await get_line_status(line_name)
    #         await message.channel.send(box(status_message))

    #     except Exception:
    #         await message.channel.send(box(
    #             "⏰ You didn’t reply in time or an error occurred. Try again."
    #         ))

    # elif content.startswith("!next train"):
    #     user_input = content.replace("!next train", "").strip()
    #     parts = user_input.split()

    #     if len(parts) >= 2:
    #         origin_raw = parts[0]
    #         dest_raw = " ".join(parts[1:])

    #         origin_norm = normalize_station(origin_raw)
    #         dest_norm = normalize_station(dest_raw)

    #         invalid_bits = []

    #         if origin_norm not in REGIONAL_RAIL_STATIONS:
    #             invalid_bits.append(f"origin station **{origin_raw}**")

    #         if dest_norm not in REGIONAL_RAIL_STATIONS:
    #             invalid_bits.append(f"destination station **{dest_raw}**")

    #         if invalid_bits:
    #             msg = (
    #                 "⚠️ I couldn't find "
    #                 + " and ".join(invalid_bits)
    #                 + " in the Regional Rail station list.\n"
    #                 "Please check the spelling, or try `/station` to look up a station."
    #             )
    #             await message.channel.send(box(msg))
    #             return

    #         await message.channel.send(box(
    #             f"Fetching the next train from **{origin_norm} → {dest_norm}**…"
    #         ))

    #         try:
    #             status_message = await get_next_train(origin_norm, dest_norm)
    #             await message.channel.send(box(status_message))
    #         except Exception:
    #             logging.exception(
    #                 "Error in /next train (one-line) origin=%s dest=%s",
    #                 origin_norm,
    #                 dest_norm,
    #             )
    #             await message.channel.send(box(
    #                 "⚠️ Sorry, something went wrong while fetching that trip.\n"
    #                 "Please double-check your station names or try again in a minute."
    #             ))
    #         return

    #     def check(m: discord.Message):
    #         return m.author == message.author and m.channel == message.channel

    #     await message.channel.send(box("What station are you getting on at?"))

    #     try:
    #         origin_msg = await bot.wait_for("message", check=check, timeout=20)
    #         origin_raw = origin_msg.content.strip()
    #         origin_norm = normalize_station(origin_raw)

    #         if origin_norm.lower() != origin_raw.lower():
    #             await message.channel.send(box(f"Did you mean **{origin_norm}**?"))

    #         await message.channel.send(box(
    #             f"➡️ Where are you going from **{origin_norm}**?")
    #         )
    #         dest_msg = await bot.wait_for("message", check=check, timeout=20)
    #         dest_raw = dest_msg.content.strip()
    #         dest_norm = normalize_station(dest_raw)

    #         if dest_norm.lower() != dest_raw.lower():
    #             await message.channel.send(box(f"Did you mean **{dest_norm}**?"))

    #         await message.channel.send(box(
    #             "Use the corrected names?\n"
    #             f"- {origin_norm}\n"
    #             f"- {dest_norm}\n"
    #             "(yes / no)"
    #         ))

    #         confirm = await bot.wait_for("message", check=check, timeout=15)
    #         ans = confirm.content.lower()

    #         if ans.startswith("y"):
    #             origin_final = origin_norm
    #             dest_final = dest_norm
    #         else:
    #             origin_final = origin_raw
    #             dest_final = dest_raw

    #         if origin_norm not in REGIONAL_RAIL_STATIONS:
    #             raise ValueError(
    #                 f"Origin station **{origin_norm}** does not exist."
    #             )

    #         if dest_norm not in REGIONAL_RAIL_STATIONS:
    #             raise ValueError(
    #                 f"Destination station **{dest_norm}** does not exist."
    #             )

    #         await message.channel.send(box(
    #             f"Fetching the next train from **{origin_final} → {dest_final}**…"
    #         ))

    #         status_message = await get_next_train(origin_final, dest_final)
    #         await message.channel.send(status_message)

    #     except asyncio.TimeoutError:
    #         await message.channel.send(box("⏰ You didn’t reply in time. Try again."))

    #     except ValueError as e:
    #         await message.channel.send(box(f"❌ {str(e)}"))

    #     except Exception as e:
    #         await message.channel.send(box(
    #             "⚠️ Something went wrong while checking the next train. "
    #             "This may be a SEPTA API issue. Please try again later."
    #         ))
    #         print("Unexpected error in /next train:", e)

    # elif "/help" in content:
    #     help_text = "**Available Commands:**\n\n"

    #     HELP_DICT = {
    #         "/help": "Shows this help menu.",
    #         "/regional rail status": "Shows live delays for all Regional Rail trains.",
    #         "/check line status": "Lets you check any specific train line.",
    #         "/next train": "Shows the next train between two stations.",
    #         "/station name": "Shows Regional Rail Lines that stop at selected station.",
    #         "/menu": "Shows the list of Regional Rail Line for user to select",
    #         "/lines": "Shows what lines serve the station",
    #         "!subscribe": "Subscribe to outage alerts for a line (e.g. !subscribe Lansdale/Doylestown).",
    #         "!unsubscribe": "Unsubscribe from outage alerts for a line.",
    #         "!mysubscriptions": "List the lines you are subscribed to.",
    #         "!subscribemenu": "Open a dropdown to pick a line to subscribe.",
    #         "!unsubscribemenu": "Open a dropdown to pick a line to unsubscribe.",
    #     }

    #     for cmd, desc in HELP_DICT.items():
    #         help_text += f"{cmd} — {desc}\n"

    #     await message.channel.send(box(help_text))

    # elif "/lines" in content:
    #     await message.channel.send(box("Which station do you want to check?"))

    #     def check(m: discord.Message):
    #         return m.author == message.author and m.channel == message.channel

    #     try:
    #         user_msg = await bot.wait_for("message", check=check, timeout=20)
    #         station_raw = user_msg.content.strip()
    #         station_norm = normalize_station(station_raw)

    #         result = await get_station_arrivals(station_norm)
    #         await message.channel.send(result)

    #     except Exception:
    #         await message.channel.send(box(
    #             "⏰ You didn’t reply in time. Try again."
    #         ))

    # NEW: handle plain-text "/subscribemenu" like the prefix command
    if content.startswith("/subscribemenu"):
        line_map = await fetch_line_station_map()
        lines = sorted(line_map.keys())

        view = SubscribeLineView(lines, message.author.id)
        await message.channel.send(
            "Select a Regional Rail **line** to subscribe to outage alerts:",
            view=view,
        )

    # NEW: handle plain-text "/unsubscribemenu" like the prefix command
    elif content.startswith("/unsubscribemenu"):
        user_id = message.author.id
        subs = await get_user_subscriptions(user_id)
        if not subs:
            await message.channel.send(box(
                f"{message.author.mention} you are not subscribed to any lines yet."
            ))
        else:
            lines = sorted(subs)
            view = UnsubscribeLineView(lines, user_id)
            await message.channel.send(
                "Select a Regional Rail **line** to unsubscribe from outage alerts:",
                view=view,
            )

    elif any(
        phrase in content
        for phrase in [
            "great job",
            "good bot",
            "awesome bot",
            "good job",
            "good work",
            "w cat",
            "awesome cat",
        ]
    ):
        user = message.author.display_name

        responses = [
            f"Thank you, {user}! 😊 I run smoother than SEPTA!",
            f"Thanks, {user}! 🚆 I’m never late… unlike SEPTA 👀",
            f"Appreciate it, {user}! 😄 My code stays on schedule!",
            f"Thank you, {user}! 🤖 I was built different.",
            f"Aww thanks, {user}! 😊 You're the real MVP.",
            f"Thanks, {user}! 🙌 I run cleaner than SEPTA’s tracks!",
            f"Cheers, {user}! 😄 My uptime > SEPTA reliability.",
            "O I I A I <<SPINNING TECHNIQUE>>",
        ]

        reply = random.choice(responses)
        await message.channel.send(reply)

        if reply == "O I I A I <<SPINNING TECHNIQUE>>":
            await message.channel.send(file=discord.File("cat_spin.gif"))
        return

    elif content in ["o i i a i", "spin", "w cat", "spin cat"]:
        await message.channel.send("O I I A I <<SPINNING TECHNIQUE>>")
        await message.channel.send(file=discord.File("cat_spin.gif"))
        return

    await bot.process_commands(message)


# ---------------------------
# Prefix commands: subscribe / unsubscribe / menus
# ---------------------------
@bot.command(name="subscribe")
async def subscribe_prefix(ctx: commands.Context, *, line_name: str):
    user_id = ctx.author.id
    await subscribe_to_line(user_id, line_name)
    await ctx.send(
        f"{ctx.author.mention} ✅ you are now subscribed to alerts for **{line_name}**."
    )


@bot.command(name="unsubscribe")
async def unsubscribe_prefix(ctx: commands.Context, *, line_name: str):
    user_id = ctx.author.id
    await unsubscribe_to_line(user_id, line_name)
    await ctx.send(
        f"{ctx.author.mention} ✅ you are unsubscribed from alerts for **{line_name}**."
    )


@bot.command(name="mysubscriptions")
async def my_subscriptions_prefix(ctx: commands.Context):
    user_id = ctx.author.id
    subs = await get_user_subscriptions(user_id)
    if not subs:
        await ctx.send(
            f"{ctx.author.mention} you are not subscribed to any lines yet. "
            "Use `!subscribe <line>` or `!subscribemenu` to get started."
        )
    else:
        lines = ", ".join(sorted(subs))
        await ctx.send(
            f"{ctx.author.mention} you are subscribed to alerts for:\n**{lines}**"
        )


@bot.command(name="subscribemenu")
async def subscribemenu_prefix(ctx: commands.Context):
    line_map = await fetch_line_station_map()
    lines = sorted(line_map.keys())

    view = SubscribeLineView(lines, ctx.author.id)
    await ctx.send(
        "Select a Regional Rail **line** to subscribe to outage alerts:",
        view=view,
    )


@bot.command(name="unsubscribemenu")
async def unsubscribemenu_prefix(ctx: commands.Context):
    user_id = ctx.author.id
    subs = await get_user_subscriptions(user_id)
    if not subs:
        await ctx.send(
            f"{ctx.author.mention} you are not subscribed to any lines yet."
        )
        return

    lines = sorted(subs)
    view = UnsubscribeLineView(lines, ctx.author.id)
    await ctx.send(
        "Select a Regional Rail **line** to unsubscribe from outage alerts:",
        view=view,
    )


# ---------------------------
# Slash: dropdown subscribe/unsubscribe
# ---------------------------
@bot.tree.command(
    name="subscribemenu",
    description="Open a dropdown to subscribe to outage alerts for a Regional Rail line.",
)
async def subscribe_menu_slash(interaction: discord.Interaction):
    line_map = await fetch_line_station_map()
    lines = sorted(line_map.keys())

    view = SubscribeLineView(lines, interaction.user.id)
    await interaction.response.send_message(
        "Select a Regional Rail **line** to subscribe to outage alerts:",
        view=view,
        ephemeral=True,
    )


@bot.tree.command(
    name="unsubscribemenu",
    description="Open a dropdown to unsubscribe from outage alerts for a Regional Rail line.",
)
async def unsubscribe_menu_slash(interaction: discord.Interaction):
    user_id = interaction.user.id
    subs = await get_user_subscriptions(user_id)
    if not subs:
        await interaction.response.send_message(
            "You are not subscribed to any lines yet. Use `/subscribemenu` first.",
            ephemeral=True,
        )
        return

    lines = sorted(subs)
    view = UnsubscribeLineView(lines, interaction.user.id)
    await interaction.response.send_message(
        "Select a Regional Rail **line** to unsubscribe from outage alerts:",
        view=view,
        ephemeral=True,
    )


# ---------------------------
# Prefix command: menu
# ---------------------------
@bot.command()
async def menu(ctx: commands.Context):
    line_map = await fetch_line_station_map()
    await ctx.send("Select a regional rail **line**:", view=LineView(line_map))


# ---------------------------
# Run bot
# ---------------------------
bot.run(token, log_handler=handler, log_level=logging.INFO)