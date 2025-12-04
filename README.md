# 🚆 SEPTA Discord Status Bot

A Discord bot that provides real-time SEPTA Regional Rail updates, next-arrival predictions, line status queries, station lookups, and outage alert subscriptions — all directly inside Discord.

Built using:

- Python    
- SEPTA APIs  
- Async I/O 

---

## 🔑 Keywords

#Discord #Bot #Transportation #Philadelphia #Python #SEPTA API

---

## 📘 Project Abstract

SEPTA (South Eastern Pennsylvania Transportation Authority) experiences frequent delays and inconsistencies that can frustrate commuters. This project provides a Discord bot that delivers real-time status updates for trains and stations, inspired by the informational (and humor-based) site **https://www.isseptafucked.com/**.

Users can interact with the bot using **slash commands** to get:

- Live line delays  
- Next arrival times  
- Station-specific schedules  
- Notifications when a subscribed line experiences an outage  

No need to install the SEPTA app because everything happens inside Discord.

---

##  High-Level Requirements

- Notify users when a subscribed train line is delayed  
- Allow users to query line-specific or station-specific information  
- Provide next-arrival predictions between two stations  
- Enable subscription to outage alerts  
- Display train line and station mappings for user convenience  

---

## ⭐ Features

- View real-time delays for any SEPTA Regional Rail line  
- Get the next train between any two Regional Rail stations  
- Look up station-specific arrival times  
- Display which lines serve a given station  
- Subscribe and unsubscribe to outage alerts for specific lines  
- Use dropdown menus for line selection to reduce typing errors  
- Handle invalid input gracefully with clear, user-friendly messages  

---

##  Background

SEPTA has faced reliability issues across several Regional Rail lines, but it exposes public APIs that allow developers to access real-time system data.

Discord is widely used among Philadelphia-area communities, making it an ideal platform to deliver transit information conveniently. This bot bridges SEPTA’s data with Discord’s interface to give commuters instant updates without opening another app or browser.

---

##  Conceptual Design

Example of how the bot would behave at its simplest form:  
https://imgur.com/a/7Zc6mB1

---

## 📁 Project Structure

```text
Discord-SEPTA-Bot/
├── main.py             # Entry point for the bot and Discord commands
├── Septa_Api.py        # Functions for calling SEPTA public APIs
├── Stations.py         # Station and line normalization / mappings
├── Select_menu.py      # Dropdown / select menu views for subscriptions
├── station_alerts.py   # Background task for alert notifications
├── requirements.txt    # Python dependencies
├── discord.log         # Runtime logs (created at runtime)
└── README.md           # Project documentation
```
---
## 📦 Installation & Setup

### 1. Clone the repository

    git clone https://github.com/Prismfade/Discord-SEPTA-Bot.git
    cd Discord-SEPTA-Bot

### 2. Create a virtual environment

    python3 -m venv venv
    source venv/bin/activate

### 3. Install dependencies

    pip install -r requirements.txt

### 4. Create a `.env` file in the project root

    DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN


### 5. Run the bot

    python3 main.py

---

## 🔧 Slash Commands

| Command                 | Description                                              |
|-------------------------|----------------------------------------------------------|
| `/help`                 | Shows all bot commands                                   |
| `/regional_rail_status` | Live delays for all Regional Rail trains                 |
| `/check_line_status`    | Check the status of a specific train line                |
| `/next_train`           | Shows the next train between two stations                |
| `/station`              | Station arrival times                                    |
| `/lines`                | Displays which lines serve a station                     |
| `/subscribemenu`        | Subscribe to outage alerts (dropdown menu)               |
| `/unsubscribemenu`      | Unsubscribe from outage alerts                           |
| `/my_subscriptions`     | Show which lines you are subscribed to                   |

---

##  Subscription Features

Users can subscribe to outage alerts for any Regional Rail line.  
The bot automatically sends updates when:

- A line becomes delayed  
- A route is suspended  
- Major disruptions occur  

Prefix-style subscription commands:

- `!subscribe <line>`  
- `!unsubscribe <line>`  
- `!mysubscriptions`  

These mirror the slash-based subscription features but are kept for backward compatibility.

---

## 🗂 Required Resources

- A **Discord Bot Token** from the [Discord Developer Portal](https://discord.com/developers/applications)  
- A server (local or cloud) to run the bot continuously  
- Python 3.10+  
- Internet access to call SEPTA APIs  

---

##  APIs Used

The bot interacts with SEPTA’s public endpoints, including but not limited to:

- **Regional Rail Status API** – Live train delays  
- **Next Train / Schedules API** – Upcoming trips between two stations  
- **Station Arrivals API** – Upcoming trains at a specific station  
- **Alerts API** – Service alerts and route suspensions  

These APIs power the real-time information shown in Discord.

---

## 👥 Team Members

- Jerry Lin  
- Christine Kapp  
- Justin Pham 
- Fares Hagos
- Chris Breeden 

---

## 📄 Notes

- The bot will **not run** without a valid Discord token in a `.env` file.  
- All sensitive data (tokens, keys, credentials) should **never** be committed to GitHub.  
- Logs are written to `discord.log` for debugging and monitoring.

---

## 🧾 License

This project is for educational purposes as part of a software engineering course.  
Future work may adapt it for broader or production use.
