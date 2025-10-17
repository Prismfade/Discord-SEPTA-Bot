Project Abstract
- With the modern landscape of SEPTA (South Eastern Pennsylvania Transportation Authority), there has been a lot of certainties about the reliability of the service.
This Discord bot service would allow updates to SEPTA transportation systems allowing users to be notified if their services are late. This project is inspired by the jokingly (but also resourceful website) https://www.isseptafucked.com/...


Requirement:
This requires the teams acknowledgement of how the Discord bot API works. Typically JS or Python is used with a few libraries such as dotenv is being used.
The bot will heavily rely on the SEPTA transportation system API that is given by SEPTA themselves for tracking: https://www3.septa.org/

Proof of concept



Keywords
#Discord #Bot #Transportation #Philadelphia #Python #SEPTA API

## Project Abstract
With the modern landscape of SEPTA (South Eastern Pennsylvania Transportation Authority), there has been a lot of certainties about the reliability of the service.
This Discord bot service would allow updates to SEPTA transportation systems allowing users to be notified if their services are late. This project is inspired by the humor centric (but also resourceful website) https://www.isseptafucked.com/
For an example, this bot can be implemented to any Discord server, especially local centered ones. All it takes is a user to type in a command such as "!Lansdale line status" to
receive information on if there is a delay on that line.

### High Level Requirement.
This requires the teams acknowledgement of how the Discord bot API works. Typically JS or Python is used with a few libraries such as dotenv.
The bot will heavily rely on the SEPTA transportation system API that is given by SEPTA themselves for tracking: https://www3.septa.org/

### Conceptual Design
This is a screenshot of how the bot would behave: https://imgur.com/a/7Zc6mB1

## Proof of Concept
Currently using Discord Bot API through Discord development portal. Need to find a way to implement SEPTA API at the current moment https://www3.septa.org/
Current GitHub repository: https://github.com/Prismfade/Discord-SEPTA-Bot
Without the secret discord bot token that I only have locally stored on my machine, the program will not run. The basic idea is that through a URL link, you can invite the Discord bot to your personal server.
While the program/code is running on an environment along with the discord bot token, users will be able to type syntax commands within a chat to get information such as regional rail statuses.

## Background
To preface the reasoning behind the project, SEPTA has been going through many problems within the last few months that are very prominent. It is hard to find delays on certain SEPTA lines, but there is API available from SEPTA that users can use that keeps track of schedules and delays of SEPTA trains.
The goal is to provide transparency to users of SEPTA, by giving them a way to check up on the status of their commute. Due to Discord being a primary platform of communications that people use, it would provide convenience to the hands of many users due to the ease of use of Discord bots.


## Required Resources
- Currently a resource that might just needed is a server to host the program to run at all times. The line of code must be running at all times in order for the bot to work. Otherwise I've been able to test the server locally through my terminal environment.
