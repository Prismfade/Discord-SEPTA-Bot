import discord
from discord.ext import commands, tasks
from discord import app_commands
from Line_Subscription import get_user_subscriptions
import aiohttp
import re
import html as html_lib

# -------- CONFIG -------- #

ALERT_CHANNEL_ID = 1437230785072463882
ALERTS_URL = "https://www3.septa.org/hackathon/Alerts/get_alert_data.php"

# Cache: { route_name_lower: "up" | "down" }
route_status_cache = {}

# Alert level options
ALERT_LEVEL_OUTAGES_ONLY = "outages"
ALERT_LEVEL_OUTAGES_AND_DELAYS = "outages_and_delays"
ALERT_LEVEL_ALL = "all_rr"


# ------------------------ #
# Helpers
# ------------------------ #

async def fetch_route_alerts():
    """Fetches alerts from SEPTA Alerts API."""
    async with aiohttp.ClientSession() as session:
        async with session.get(ALERTS_URL) as resp:
            resp.raise_for_status()
            return await resp.json()


def extract_alert_message(alert_obj):
    """Pick the most important alert field available."""
    return (
        (alert_obj.get("current_message") or "").strip()
        or (alert_obj.get("advisory_message") or "").strip()
        or (alert_obj.get("detour_message") or "").strip()
    )


def clean_alert_text(text: str) -> str:
    """
    Convert SEPTA's HTML alert text into nice, readable plain text
    for Discord messages / embeds.
    """
    if not text:
        return ""

    # Decode HTML entities (&nbsp;, &amp;, etc.)
    text = html_lib.unescape(text)

    # <a href="url">text</a> -> "text (url)"
    def repl_a(match):
        href = match.group(1)
        inner_html = match.group(2)
        inner_text = re.sub(r"<[^>]+>", "", inner_html)
        inner_text = inner_text.strip() or href
        return f"{inner_text} ({href})"

    text = re.sub(
        r'<a\s+[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
        repl_a,
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )

    # Basic formatting tags to line breaks / bullets
    text = re.sub(r"<\s*br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</\s*p\s*>", "\n\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</\s*h[1-6]\s*>", "\n\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<\s*li\s*>", "• ", text, flags=re.IGNORECASE)

    # Strip remaining tags
    text = re.sub(r"<[^>]+>", "", text)

    # Clean up whitespace
    text = re.sub(r"\r", "", text)
    text = re.sub(r"\n\s+\n", "\n\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)

    return text.strip()


def is_regional_rail(alert_obj) -> bool:
    """
    Heuristic filter: return True only for Regional Rail routes.
    Excludes MFL, BSL, NHSL, trolleys, bus, etc.
    """
    name = (alert_obj.get("route_name") or "").lower()

    metro_keywords = [
        "market-frankford",
        "market frankford",
        "broad street",
        "norristown high speed",
        "owl",
        "trolley",
        "metro",
        "bus",
    ]
    if any(k in name for k in metro_keywords):
        return False

    return True


def is_impactful_alert(text: str, level: str) -> bool:
    """
    Decide if this alert should be surfaced based on alert level:

      - outages:            only "no service", "suspended", etc.
      - outages_and_delays: outages + specific delays (train # or minutes)
      - all_rr:             any RR alert with non-empty text
    """
    if not text:
        return False

    t = text.lower()

    # Strong "down" / no service (always counts)
    severe_keywords = [
        "no service",
        "suspended",
        "suspension",
        "not operating",
        "not in service",
        "shut down",
        "shutdown",
        "out of service",
        "cancelled",
        "canceled",
        "service has been suspended",
    ]
    if any(k in t for k in severe_keywords):
        return True

    if level == ALERT_LEVEL_OUTAGES_ONLY:
        return False

    # Delays
    delay_keywords = ["delay", "delays", "delayed", "late", "running late"]
    if any(k in t for k in delay_keywords):
        if level == ALERT_LEVEL_OUTAGES_AND_DELAYS:
            # require train number or minutes to avoid generic spam
            has_train_number = bool(re.search(r"#\d{3,4}", text))
            has_minutes = bool(re.search(r"\d+\s*(min|mins|minutes)", t))
            if has_train_number or has_minutes:
                return True
            return False
        elif level == ALERT_LEVEL_ALL:
            # any delay is fine here
            return True

    if level == ALERT_LEVEL_ALL:
        # any non-empty RR alert
        return True

    return False


# ------------------------ #
# Cog
# ------------------------ #

class StationAlerts(commands.Cog):
    """Automatic route alert monitoring (Regional Rail only, via SEPTA Alerts API)."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Default alert level: outages + specific delays
        self.alert_level = ALERT_LEVEL_OUTAGES_AND_DELAYS
        self.poll_routes_for_outages.start()

    def cog_unload(self):
        self.poll_routes_for_outages.cancel()

    # ----- Find subscribers for a route ----- #
    async def get_subscriber_mentions(self, route_name: str):
        key = route_name.lower()
        mentions = []

        for guild in self.bot.guilds:
            for member in guild.members:
                if member.bot:
                    continue

                try:
                    subs = await get_user_subscriptions(member.id)
                except Exception:
                    continue

                subs_lower = [s.lower() for s in subs]
                if key in subs_lower:
                    mentions.append(member.mention)

        return mentions

    # ----- Sending alerts ----- #
    async def notify_route_alert(self, route_name: str, alert_text: str):
        """Send a nicely formatted embed when a route gets a new alert."""
        channel = self.bot.get_channel(ALERT_CHANNEL_ID)
        if channel is None:
            return

        clean_text = clean_alert_text(alert_text)
        short_text = clean_text if len(clean_text) <= 1024 else clean_text[:1021] + "..."

        mentions = await self.get_subscriber_mentions(route_name)

        if mentions:
            content = " ".join(mentions)
            footer_text = None
        else:
            content = "_No subscribers for this route yet._"
            footer_text = None

        embed = discord.Embed(
            title=f"🚆 Service Alert: {route_name}",
            description=short_text,
            color=0xFF9900,
        )
        embed.set_footer(text=footer_text or "Live data from SEPTA Alerts API.")

        await channel.send(content=content, embed=embed)

    # ----- Background task ----- #
    @tasks.loop(seconds=90)
    async def poll_routes_for_outages(self):
        """Checks SEPTA Alerts feed every 90 seconds (Regional Rail only)."""
        try:
            alerts = await fetch_route_alerts()
        except Exception:
            return

        for alert in alerts:
            if not is_regional_rail(alert):
                continue

            route_name = (alert.get("route_name") or "").strip()
            if not route_name:
                continue

            raw_msg = extract_alert_message(alert)
            clean_msg = clean_alert_text(raw_msg)

            if not is_impactful_alert(clean_msg, self.alert_level):
                route_status_cache[route_name.lower()] = "up"
                continue

            previous = route_status_cache.get(route_name.lower(), "up")
            now = "down"
            route_status_cache[route_name.lower()] = now

            if now == "down" and previous != "down":
                await self.notify_route_alert(route_name, raw_msg)

    @poll_routes_for_outages.before_loop
    async def before_poll(self):
        await self.bot.wait_until_ready()

    # ---------------------------------------
    # /alerts slash command (Regional Rail)
    # ---------------------------------------
    @app_commands.command(
        name="alerts",
        description="Show current Regional Rail service alerts from SEPTA (based on alert level).",
    )
    async def alerts_slash(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        try:
            alerts = await fetch_route_alerts()
        except Exception:
            await interaction.followup.send(
                "⚠️ Could not reach SEPTA Alerts API. Please try again in a moment.",
                ephemeral=True,
            )
            return

        rr_alerts = []
        for alert in alerts:
            if not is_regional_rail(alert):
                continue

            route_name = (alert.get("route_name") or "").strip()
            if not route_name:
                continue

            raw_msg = extract_alert_message(alert)
            clean_msg = clean_alert_text(raw_msg)
            if not is_impactful_alert(clean_msg, self.alert_level):
                continue

            rr_alerts.append((route_name, clean_msg))

        mode_label = {
            ALERT_LEVEL_OUTAGES_ONLY: "Outages only",
            ALERT_LEVEL_OUTAGES_AND_DELAYS: "Outages + specific delays",
            ALERT_LEVEL_ALL: "All Regional Rail alerts",
        }.get(self.alert_level, "Unknown")

        embed = discord.Embed(
            title="🚆 Regional Rail Issues",
            description=(
                f"Current alert level: **{mode_label}**\n"
                "I show lines that are **down or having issues** on Regional Rail.\n"
                "I can also check train delays, next arrivals, station outages, and more.\n"
                "Type `!help` to get started.\n\n"
                "Live data from SEPTA Alerts API."
            ),
            color=0x0099FF,
        )

        if not rr_alerts:
            embed.add_field(
                name="All Clear ✅",
                value="No active Regional Rail alerts for this alert level.",
                inline=False,
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        for route_name, msg in rr_alerts[:10]:
            short_msg = msg if len(msg) <= 1024 else msg[:1021] + "..."
            embed.add_field(
                name=f"🚆 {route_name}",
                value=short_msg,
                inline=False,
            )

        if len(rr_alerts) > 10:
            embed.set_footer(
                text=f"And {len(rr_alerts) - 10} more impactful alerts not shown."
            )

        await interaction.followup.send(embed=embed, ephemeral=True)

    # ---------------------------------------
    # !alerts – prefix command
    # ---------------------------------------
    @commands.command(name="alerts")
    async def alerts_prefix(self, ctx: commands.Context):
        try:
            alerts = await fetch_route_alerts()
        except Exception:
            await ctx.send(
                "⚠️ Could not reach SEPTA Alerts API. Please try again in a moment."
            )
            return

        rr_alerts = []
        for alert in alerts:
            if not is_regional_rail(alert):
                continue

            route_name = (alert.get("route_name") or "").strip()
            if not route_name:
                continue

            raw_msg = extract_alert_message(alert)
            clean_msg = clean_alert_text(raw_msg)
            if not is_impactful_alert(clean_msg, self.alert_level):
                continue

            rr_alerts.append((route_name, clean_msg))

        mode_label = {
            ALERT_LEVEL_OUTAGES_ONLY: "Outages only",
            ALERT_LEVEL_OUTAGES_AND_DELAYS: "Outages + specific delays",
            ALERT_LEVEL_ALL: "All Regional Rail alerts",
        }.get(self.alert_level, "Unknown")

        embed = discord.Embed(
            title="🚆 Regional Rail Issues",
            description=(
                f"Current alert level: **{mode_label}**\n"
                "I show lines that are **down or having issues** on Regional Rail.\n"
                "I can also check train delays, next arrivals, station outages, and more.\n"
                "Type `!help` to get started.\n\n"
                "Live data from SEPTA Alerts API."
            ),
            color=0x0099FF,
        )

        if not rr_alerts:
            embed.add_field(
                name="All Clear ✅",
                value="No active Regional Rail alerts for this alert level.",
                inline=False,
            )
            await ctx.send(embed=embed)
            return

        for route_name, msg in rr_alerts[:10]:
            short_msg = msg if len(msg) <= 1024 else msg[:1021] + "..."
            embed.add_field(
                name=f"🚆 {route_name}",
                value=short_msg,
                inline=False,
            )

        if len(rr_alerts) > 10:
            embed.set_footer(
                text=f"And {len(rr_alerts) - 10} more impactful alerts not shown."
            )

        await ctx.send(embed=embed)

    # ---------------------------------------
    # !setalertlevel – opens dropdown menu
    # ---------------------------------------
    @commands.command(name="setalertlevel")
    async def set_alert_level_menu(self, ctx: commands.Context):
        """
        Open a dropdown menu to choose alert level.
        Usage: !setalertlevel
        """
        view = AlertLevelView(self)
        await ctx.send(
            "Choose how sensitive you want Regional Rail alerts to be:",
            view=view,
        )

    # ---------------------------------------
    # TEST ALERT COMMAND
    # ---------------------------------------
    @commands.command(name="testalert")
    async def testalert(self, ctx: commands.Context):
        fake_route = "Test Route"
        fake_text = (
            "Service has been suspended on this line due to an emergency. "
            "Riders should expect no service for at least 30 minutes."
        )
        await self.notify_route_alert(fake_route, fake_text)
        await ctx.send("✅ Test alert sent to the alert channel.")


# ---------- UI: Dropdown View for !setalertlevel ---------- #

class AlertLevelView(discord.ui.View):
    def __init__(self, cog: StationAlerts, *, timeout: float | None = 60):
        super().__init__(timeout=timeout)
        self.cog = cog

    @discord.ui.select(
        placeholder="Select alert level...",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                label="Outages only",
                description="Only show suspended/no service outages.",
                value=ALERT_LEVEL_OUTAGES_ONLY,
                emoji="🛑",
            ),
            discord.SelectOption(
                label="Outages + specific delays",
                description="Outages plus delays with train # or minutes.",
                value=ALERT_LEVEL_OUTAGES_AND_DELAYS,
                emoji="⚠️",
            ),
            discord.SelectOption(
                label="All Regional Rail alerts",
                description="Every Regional Rail alert from SEPTA.",
                value=ALERT_LEVEL_ALL,
                emoji="📢",
            ),
        ],
    )
    async def select_callback(
        self,
        interaction: discord.Interaction,
        select: discord.ui.Select,
    ):
        chosen = select.values[0]
        self.cog.alert_level = chosen

        mode_label = {
            ALERT_LEVEL_OUTAGES_ONLY: "Outages only",
            ALERT_LEVEL_OUTAGES_AND_DELAYS: "Outages + specific delays",
            ALERT_LEVEL_ALL: "All Regional Rail alerts",
        }.get(chosen, "Unknown")

        # Disable dropdown after selection
        for child in self.children:
            child.disabled = True

        try:
            await interaction.message.edit(view=self)
        except Exception:
            pass

        await interaction.response.send_message(
            f"✅ Alert level set to **{mode_label}**.\n"
            "This affects background alerts and `!alerts` / `/alerts`.",
            ephemeral=True,
        )


# ----- setup() required for extensions ----- #
async def setup(bot: commands.Bot):
    await bot.add_cog(StationAlerts(bot))