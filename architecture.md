# SEPTA Discord Status Bot – Architecture

This document describes the internal structure of the SEPTA Discord Status Bot and how the main components interact.

---

## 1. High-Level Overview

The bot is a Python application that:

- Connects to Discord using `discord.py`
- Calls SEPTA’s public APIs to fetch real-time transit data
- Exposes slash commands and prefix commands for users
- Runs a background task to send outage / alert notifications to subscribers

At a high level:

- **Discord** → sends user commands and events  
- **Bot (main.py)** → parses commands and coordinates logic  
- **SEPTA API module** → fetches live data  
- **Stations / mapping modules** → normalize and map station / line names  
- **Subscription & alerts modules** → track user subscriptions and send notifications  

---

## 2. Main Modules

### `main.py`
- Entry point for the application.
- Creates the `commands.Bot` instance (`MyBot`).
- Registers **slash commands**:
  - `/regional_rail_status`
  - `/check_line_status`
  - `/next_train`
  - `/station`
  - `/lines`
  - `/subscribemenu`
  - `/unsubscribemenu`
  - `/my_subscriptions`
  - `/help`
- Registers **prefix commands**:
  - `!subscribe`, `!unsubscribe`, `!mysubscriptions`
  - `!subscribemenu`, `!unsubscribemenu`
- Handles the `on_message` event:
  - Responds to “good bot”-style messages
  - Handles text versions of `/subscribemenu` and `/unsubscribemenu`
- On startup (`on_ready`), syncs global commands and posts a welcome message.

### `Septa_Api.py`
- Responsible for calling SEPTA’s public endpoints.
- Key responsibilities:
  - Fetch **regional rail status** (all trains)
  - Get **line status** for a specific line
  - Get **next train** between two stations
  - Get **arrivals** for a given station
  - Build **station → line** mappings
- Returns **formatted text strings** that can be directly wrapped in a code block and sent to Discord.

### `Stations.py`
- Holds canonical lists of:
  - `REGIONAL_RAIL_STATIONS`
- Provides utilities such as:
  - `normalize_station(name)` – normalizes user input (case / spacing) to a canonical station name.

### `dynamic_station.py`
- Builds a **line → station** mapping dynamically from API data.
- Provides:
  - `fetch_line_station_map()` – used by dropdown menus and the `/subscribemenu` UI.

### `Line_Subscription.py`
- Manages user subscriptions to Regional Rail lines.
- Key functions:
  - `subscribe_to_line(user_id, line_name)`
  - `unsubscribe_to_line(user_id, line_name)`
  - `get_user_subscriptions(user_id)`
  - `notify_line(line_name, message)` – send alert messages to all subscribers of a given line.
- Stores subscriptions in `user_line_subscriptions` (currently an in-memory structure; can be swapped for a database later).

### `Select_menu.py`
- Defines Discord **UI Views** used for dropdown menus in the bot.
- Example: `LineView` – lets users pick a Regional Rail line from a select menu.
- Used by:
  - `!menu`
  - `!subscribemenu` / `/subscribemenu`
  - `!unsubscribemenu` / `/unsubscribemenu`

### `station_alerts.py`
- Implements the `StationAlerts` **Cog**.
- Runs a background loop that:
  - Polls SEPTA alerts API
  - Detects outages / changes
  - Calls `notify_line(...)` from `Line_Subscription.py` to push alerts to subscribers.

### `requirements.txt`
- Lists Python dependencies needed to run the project.

### `discord.log`
- Created at runtime.
- Stores logs for debugging and monitoring.

---

## 3. Typical Flows

### 3.1 `/check_line_status`

1. User runs `/check_line_status`.
2. `main.py`:
   - Prompts the user in Discord: _“Which train line would you like to check?”_
   - Waits for the user’s reply in the same channel.
3. Once the user replies, `main.py`:
   - Calls `get_line_status(line_name)` in `Septa_Api.py`.
   - Wraps the returned status text in a code block and replies to the user.
4. If anything fails (timeout or error), user sees a friendly error message.

### 3.2 Subscribing to Outage Alerts

1. User runs `/subscribemenu` or `!subscribemenu`.
2. `main.py`:
   - Calls `fetch_line_station_map()` from `dynamic_station.py` to get an updated list of lines.
   - Builds a `SubscribeLineView` dropdown with those lines.
3. User selects a line from the dropdown.
4. `SubscribeLineView`:
   - Calls `subscribe_to_line(user_id, line_name)` in `Line_Subscription.py`.
   - Updates the original message to confirm the subscription.

### 3.3 Alert Notifications

1. `StationAlerts` cog starts a background loop when the bot is ready.
2. On each cycle:
   - It polls SEPTA alerts endpoints via `Septa_Api.py`.
   - Compares current alerts with previous ones.
3. For each affected line:
   - Calls `notify_line(line_name, message)` from `Line_Subscription.py`.
   - That function looks up all subscribers and sends a DM / message to each user.

---

## 4. Future Improvements

Some possible next steps for the architecture:

- Persist subscriptions in a database (e.g., SQLite, MongoDB, or Postgres).
- Add more robust error handling and retries around SEPTA API calls.
- Cache SEPTA responses to reduce API load.
- Add unit tests for:
  - Station normalization
  - Subscription logic
  - SEPTA API formatting functions
