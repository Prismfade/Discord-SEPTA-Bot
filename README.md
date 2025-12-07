<!-- Template Source: https://github.com/othneildrew/Best-README-Template -->

<a id="readme-top"></a>
<p align="center">
  <img src="README Assets/Screenshot2.png" alt="Banner" width="100%" />
</p>


<!-- PROJECT SHIELDS -->
<a href="https://github.com/Prismfade/Discord-SEPTA-Bot/graphs/contributors"><img src="README Assets/Contributor-Shield.png" width="120" height="30" alt="Contributors 5"></a>
<a href=" "><img src="README Assets/Linkedin-Shield1.png" width="100" height="30" alt="Linkedin Shield 1"></a>
<a href="https://www.linkedin.com/in/christine-kapp-658b41238"><img src="README Assets/Linkedin-Shield2.png" width="100" height="30" alt="Linkedin Shield 2"></a>
<a href=" "><img src="README Assets/Linkedin-Shield3.png" width="100" height="30" alt="Linkedin Shield 3"></a>
<a href=" "><img src="README Assets/Linkedin-Shield4.png" width="100" height="30" alt="Linkedin Shield 4"></a>
<a href="https://www.linkedin.com/in/justinphams/"><img src="README Assets/Linkedin-Shield5.png" width="100" height="30" alt="Linkedin Shield 5"></a>
<a href=" "><img src="README Assets/Linkedin-Shield6.png" width="100" height="30" alt="Linkedin Shield 6"></a>


<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/Prismfade/Discord-SEPTA-Bot">
    <img src="README Assets/logo.png" alt="Logo" width="200" height="200">
  </a>

  <h3 align="center">SEPTA Discord Bot</h3>

  <p align="center">
    A bot that brings real-time SEPTA Regional Rail data straight into your Discord server.
    <br />
    <a href="https://github.com/Prismfade/Discord-SEPTA-Bot"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href=" ">View Demo</a> <!-- TO-DO: Insert unlisted video demo link here -->
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
        <li><a href="#overview">Overview</a></li>
        <li><a href="#key-features">Key Features</a></li>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
        <ul>
        <li><a href="#live-status-and-rail-information">Live Status and Rail Information</a></li>
        <li><a href="#subscription-and-alert-management">Subscription and Alert Management</a></li>
        </ul>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

<p align="left"><a href=" " ><img src="README Assets/Chat-Screenshot.jpeg" width="100%" height="100%" alt="Demo Video"></a></p>

### ⭐️ Overview

This bot provides **live SEPTA Regional Rail updates** directly inside Discord — delays, cancellations, arrival times, outages, and station alerts — all pulled from the official SEPTA Regional Rail API’s real-time JSON feeds. It’s built for commuters, Philly-based servers, transit enthusiasts, and anyone who wants **accurate train information** without opening a website or app. Every response is formatted as a **clean Discord embed**, and users interact with the bot through slash commands, dropdown menus, autocompleted options, and classic prefix commands.

Beyond one-off status checks, the bot functions like a **personal transit assistant**. Users can **subscribe to specific lines** and automatically receive **background-pushed outage alerts** as soon as the API updates — no refreshing, no searching, no guessing.

---

### 🔍 Key Features

* **Live Network Status:** Provides a full Regional Rail system's current snapshot.
* **Line-Specific Checks:** Get detailed status, including delays, canceled trips, and severe disruptions.
* **Station Arrivals:** View upcoming trains and estimated times of arrival (ETAs) for any station.
* **Route Finding:** Quickly find the next available train between two specified stations.
* **Station-to-Line Lookup:** See exactly which Regional Rail lines serve a given location.
* **Interactive Subscriptions:** Use dropdown menus to easily subscribe/unsubscribe from outage notifications.
* **Automatic Alerts:** Receive **background-pushed outage alerts** posted into a designated Discord channel.
* **Seamless Interaction:** Includes **Autocomplete support** to prevent station name typos and minimize input errors.
* **Personality:** Features fun, personality-based responses and small easter-egg interactions.

---

### 🔨 Built With

* <a href="https://www.python.org"><img src="README Assets/python-logo.png" width="120" height="40" alt="Python"></a>
* <a href="https://docs.aiohttp.org/en/stable"><img src="README Assets/aiohttp-logo.png" width="120" height="40" alt="Aiohttp"></a>
* <a href="https://api.septa.org"><img src="README Assets/septa-logo.jpeg" width="120" height="40" alt="Septa"></a>
* <a href="https://discordpy.readthedocs.io/en/stable"><img src="README Assets/discord-logo.png" width="120" height="40" alt="Discord"></a>
* <a href="https://cybrancee.com/discord-bot-hosting"><img src="README Assets/cybrancee-logo.png" width="120" height="40" alt="Cybranceee"></a>

---

<!-- INVITE BOT TO SERVER -->
### Invite Bot to Server

Scan the QR Code to add SEPTA Discord Bot to your server.

<img src="README Assets/qr-code.png" width="200" height="200" alt="QR Code"></a>


<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

To get a local copy of SEPTA Discord Bot up and running follow these simple steps.

### ⚠️ Prerequisites

* pip
  ```sh
  pip install python-dotenv # or pip3 install python-dotenv 
  ```

* pip
  ```sh
  pip install discord.py # or /Applications/Python\ 3.13/Install\ Certificates.command
  ```

### 🧱 Installation

1. Create your personal API Key
   ```sh
   xxx
   ```

2. Clone the repo
   ```sh
   git clone https://github.com/Prismfade/Discord-SEPTA-Bot.git
   ```

3. Enter your API in `config.js`
   ```js
   const API_KEY = 'your_API_key';
   ```

4. Change git remote url to avoid accidental pushes to base project
   ```sh
   git remote set-url origin https://github.com/Prismfade/Discord-SEPTA-Bot
   git remote -v # confirm the changes
   ```

5. Run main.py to start the bot
    ```sh
    python main.py # or python3 main.py
                   # or .venv\Scripts\activate before python main.py
    ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- USAGE EXAMPLES -->
## Usage

The bot supports modern **Slash Commands** (prefixed with `/`).

### 📊 Live Status and Rail Information

| Command | Type | Description | Example Usage |
| :--- | :--- | :--- | :--- |
| **`/regional_rail_status`** | Slash | Shows **live delays** on all Regional Rail trains. | `/regional_rail_status` |
| **`/check_line_status`** `name` | Slash | Checks the **status of a specific train line**. | `/check_line_status name:Lansdale/Doylestown` |
| **`/next_train`** `origin` `destination` | Slash | Finds the **next train** between two stations. | `/next_train origin:30th Street Station destination:Suburban Station` |
| **`/station`** `name` | Slash | Gets the next **arrival times for a specific station**. | `/station name:Temple University` |
| **`/lines`** | Slash | Finds out **what lines serve a station**. | `/lines` |
| **`/help`** | Slash | Shows a list of **all available commands**. | `/help` |

### 🔔 Subscription and Alert Management

These commands manage real-time outage alerts for specific Regional Rail lines.

| Command | Type | Description | Example Usage |
| :--- | :--- | :--- | :--- |
| **`/my_subscriptions`** | Slash | Shows which lines you are currently **subscribed** to. | `/my_subscriptions` |
| **`/subscribe_line`** `line_name` | Slash | **Subscribe** to outage alerts (requires exact line name). | `/subscribe_line line_name:Trenton` |
| **`/unsubscribe_line`** `line_name` | Slash | **Unsubscribe** from outage alerts. | `/unsubscribe_line line_name:Paoli/Thorndale` |
| **`/subscribemenu`** | Slash / Text | Opens a **dropdown menu** to easily select and subscribe. | `/subscribemenu` |
| **`/unsubscribemenu`** | Slash / Text | Opens a **dropdown menu** to easily select and unsubscribe. | `/unsubscribemenu` |

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* <a href="https://github.com/othneildrew/Best-README-Template"><img src="README Assets/best-readme-template.png" width="120" height="40" alt="Best README Template"></a>
* <a href="https://www.isseptafucked.com"><img src="README Assets/is-septa-fucked-logo.png" width="120" height="40" alt="Is SEPTA Fucked"></a>
* <a href="https://www3.septa.org"><img src="README Assets/septa-logo.jpeg" width="120" height="40" alt="SEPTA"></a>


<p align="right">(<a href="#readme-top">back to top</a>)</p>
