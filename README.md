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
<a href=" "><img src="README Assets/Linkedin-Shield5.png" width="100" height="30" alt="Linkedin Shield 5"></a>
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
    <a href=" ">View Demo</a>
    &middot;
    <a href=" ">Report Bug</a>
    &middot;
    <a href=" ">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
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
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

<p align="left"><a href=" " ><img src="README Assets/Chat-Screenshot.jpeg" width="100%" height="100%" alt="Demo Video"></a></p>

### 📌 Overview

This bot provides live SEPTA Regional Rail updates directly inside Discord — delays, cancellations, arrival times, outages, and station alerts — all pulled from the official SEPTA Regional Rail API’s real-time JSON feeds.

It’s built for commuters, Philly-based servers, transit enthusiasts, and anyone who wants accurate train information without opening a website or app. Every response is formatted as a clean Discord embed, and users interact with the bot through slash commands, dropdown menus, autocompleted options, and classic prefix commands.

Beyond one-off status checks, the bot functions like a personal transit assistant. Users can subscribe to specific lines and automatically receive background-pushed outage alerts as soon as the API updates — no refreshing, no searching, no guessing.

### 🔍 What It Can Do

* Live network snapshot showing the full Regional Rail system’s current state
* Line-specific status checks (delays, canceled trips, severe disruptions)
* Station arrival boards with upcoming trains and ETAs
* Route finder showing the next available train between two stations
* Station → line lookup so users see what lines serve a given location
* Interactive dropdown menus for subscribing/unsubscribing to outage notifications
* Automatic background alerts posted into a designated Discord channel
* Autocomplete support to prevent station name typos
* Fun, personality-based responses and small easter-egg interactions

<!-- Original README -->
<!--## Keywords 

#Discord #Bot #Transportation #Philadelphia #Python #SEPTA API

## Project Abstract

With the modern landscape of SEPTA (South Eastern Pennsylvania Transportation Authority), there has been a lot of certainties about the reliability of the service. This Discord bot service would allow updates to SEPTA transportation systems allowing users to be notified if their services are late. This project is inspired by the humor centric (but also resourceful website) https://www.isseptafucked.com/ For an example, this bot can be implemented to any Discord server, especially local centered ones. All it takes is a user to type in a command such as "!Lansdale line status" to receive information on if there is a delay on that line. The goal is to provide commuters a tool they can use on a familiar platform such as Discord, access to information about SEPTA without having to install the SEPTA application. Providing features such as late times, ways to subscribe to notifications, and even prospect routes based on user inputs.

## High Level Requirement

- Notify users if a subscribed form of transportation is late
- Allow users to find nearest regional rail route to get to destiation
- Provide estimated notifications for both subway lines and trolley

## Conceptual Design

This is a screenshot of how the bot would behave at its simplest form: https://imgur.com/a/7Zc6mB1

## Proof of Concept

Like mentioned in the abstract, https://www.isseptafucked.com/ was an inspiration for this project proposal. According to their documentation, they use SEPTAs API to receive all of the data required to track late times of trains. On their FAQ, they mentioned that with using node.js, they were able to asynchronously sync "data from SEPTA's API in the same process, without having to use crontabs. Or a even database for that matter."

Currently using Discord Bot API through Discord development portal. Will need to find a way to implement SEPTA API https://www3.septa.org/.

Current GitHub repository: https://github.com/Prismfade/Discord-SEPTA-Bot Without the secret discord bot token that I only have locally stored on my machine, the program will not run. The basic idea is that through a URL link, you can invite the Discord bot to your personal server. While the program/code is running on an environment along with the discord bot token, users will be able to type syntax commands within a chat to get information such as regional rail statuses.

## Background

To preface the reasoning behind the project, SEPTA has been going through many problems within the last few months that are very prominent. It is hard to find delays on certain SEPTA lines, but there is API available from SEPTA that users can use that keeps track of schedules and delays of SEPTA trains. The goal is to provide transparency to users of SEPTA, by giving them a way to check up on the status of their commute. Due to Discord being a primary platform of communications that people use, it would provide convenience to the hands of many users due to the ease of use of Discord bots.

## Required Resources

Currently a resource that might just needed is a server to host the program to run at all times. The line of code must be running at all times in order for the bot to work. Otherwise I've been able to test the server locally through my terminal environment.-->



### 🔨 Built With

This section should list any major frameworks/libraries used to bootstrap your project. Leave any add-ons/plugins for the acknowledgements section. Here are a few examples.

* <a href="https://www.python.org"><img src="README Assets/python-logo.png" width="120" height="40" alt="Python"></a>
* <a href="https://docs.aiohttp.org/en/stable"><img src="README Assets/aiohttp-logo.png" width="120" height="40" alt="Aiohttp"></a>
* <a href="https://api.septa.org"><img src="README Assets/septa-logo.jpeg" width="120" height="40" alt="Septa"></a>
* <a href="https://discordpy.readthedocs.io/en/stable"><img src="README Assets/discord-logo.png" width="120" height="40" alt="Discord"></a>

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

This is an example of how you may give instructions on setting up your project locally.
To get a local copy up and running follow these simple example steps.

### Prerequisites

This is an example of how to list things you need to use the software and how to install them.
* npm
  ```sh
  npm install npm@latest -g
  ```

### Installation

_Below is an example of how you can instruct your audience on installing and setting up your app. This template doesn't rely on any external dependencies or services._

1. Get a free API Key at [https://example.com](https://example.com)
2. Clone the repo
   ```sh
   git clone https://github.com/Prismfade/Discord-SEPTA-Bot.git
   ```
3. Install NPM packages
   ```sh
   npm install
   ```
4. Enter your API in `config.js`
   ```js
   const API_KEY = 'xxx';
   ```
5. Change git remote url to avoid accidental pushes to base project
   ```sh
   git remote set-url origin github_username/repo_name
   git remote -v # confirm the changes
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

Use this space to show useful examples of how a project can be used. Additional screenshots, code examples and demos work well in this space. You may also link to more resources.

_For more examples, please refer to the [Documentation](https://example.com)_

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the Unlicense License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Your Name - [@your_twitter](https://twitter.com/your_username) - email@example.com

Project Link: [https://github.com/your_username/repo_name](https://github.com/your_username/repo_name)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

Use this space to list resources you find helpful and would like to give credit to. I've included a few of my favorites to kick things off!

* <a href="https://github.com/othneildrew/Best-README-Template"><img src=" " width="120" height="30" alt="Best README Template"></a>
* <a href="https://www.isseptafucked.com"><img src=" " width="120" height="30" alt="Is SEPTA Fucked"></a>
* <a href="https://www3.septa.org"><img src=" " width="120" height="30" alt="SEPTA"></a>


<p align="right">(<a href="#readme-top">back to top</a>)</p>