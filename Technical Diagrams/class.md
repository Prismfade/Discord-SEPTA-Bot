
```mermaid
classDiagram

    class MyBot {
        +command_prefix: "/"
        +intents
        +setup_hook()
        +bg_task
    }

    class SelectMenu {
        <<abstract>>
        +callback(interaction)
    }

    class LineView {
        +line_map
        +buttons
    }

    class SubscribeLineView {
        +line_names
        +callback()
    }

    class UnsubscribeLineView {
        +user_subscriptions
        +callback()
    }

    class SeptaApi {
        +get_regional_rail_status()
        +get_line_status(line)
        +get_next_train(origin, dest)
        +get_station_arrivals(station)
        +get_unique_regional_rail_lines()
        +build_station_line_map()
    }

    class Aiohttp {
        <<library>>
        +ClientSession()
        +get(url)
        +json()
    }

    class SubscriptionSystem {
        +user_line_subscriptions: dict
        +get_user_subscriptions(user_id)
        +notify_line(bot, line, status)
    }

    class Stations {
        +normalize_station(name)
        +REGIONAL_RAIL_STATIONS
    }

    class BotEvents {
        +on_ready()
        +on_message(message)
    }

    class DiscordPy {
        <<framework>>
        app_commands
        events
    }

    %% Relationships
    MyBot --> BotEvents
    MyBot --> SelectMenu
    SelectMenu <|-- LineView
    SelectMenu <|-- SubscribeLineView
    SelectMenu <|-- UnsubscribeLineView

    MyBot --> SeptaApi
    MyBot --> SubscriptionSystem
    MyBot --> Stations
    MyBot --> DiscordPy

    SeptaApi --> Aiohttp : "uses"