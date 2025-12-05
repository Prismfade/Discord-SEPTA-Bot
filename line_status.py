import discord
from discord.ext import commands, tasks
import aiohttp
from Line_Subscription import notify_line, get_user_subscriptions

# Route: TrainView endpoint
TRAINS_URL = "https://www3.septa.org/api/TrainView/index.php"

# Cache format:
# { "Lansdale/Doylestown": {"trainno": {"delay": 5, "status": "late"}} }
line_delay_cache = {}

# Map API "line" to correct canonical line name from your normalize_line() list
# Example: SEPTA calls it "Lansdale/Doylestown" exactly, so this is safe.
def canonicalize(line_name: str):
    return line_name.title().strip()


class LineStatusMonitor(commands.Cog):
    """
    Monitors delays/cancellations on Regional Rail lines.
    Notifies subscribers when status changes.
    """

    def __init__(self, bot):
        self.bot = bot
        self.poll_line_status.start()

    def cog_unload(self):
        self.poll_line_status.cancel()

    @tasks.loop(seconds=90)
    async def poll_line_status(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(TRAINS_URL) as resp:
                    trains = await resp.json()
        except Exception:
            return  # do nothing if API fails

        # reorganize trains by line
        lines = {}
        for t in trains:
            line = canonicalize(t.get("line", ""))
            delay = int(t.get("late", 0))
            trainno = t.get("trainno", "N/A")

            if not line:
                continue

            lines.setdefault(line, {})
            lines[line][trainno] = delay

        # Now check each line for status changes
        for line_name, trains_dict in lines.items():
            old_data = line_delay_cache.get(line_name, {})

            for trainno, delay in trains_dict.items():
                old_delay = old_data.get(trainno)

                # NEW delay OR HUGE change
                if old_delay != delay:
                    # Skip on-time → on-time changes
                    if delay == 0 and old_delay == 0:
                        continue

                    # Build message
                    if delay >= 500:
                        msg = f"❌ Train **{trainno}** on **{line_name}** has been *CANCELED*."
                    elif delay == 0:
                        msg = f"✅ Train **{trainno}** on **{line_name}** is now back **on time**."
                    elif delay <= 5:
                        msg = f"⚠️ Train **{trainno}** on **{line_name}** is running **{delay} minutes late**."
                    else:
                        msg = f"⛔ Train **{trainno}** on **{line_name}** is **{delay} minutes late**."

                    # DM all subscribers
                    await notify_line(self.bot, line_name, msg)

            # update cache
            line_delay_cache[line_name] = trains_dict

    @poll_line_status.before_loop
    async def before_poll(self):
        await self.bot.wait_until_ready()
