
```mermaid
classDiagram

    class MyBot {
        +intents
        +setup_hook()
    }

    

    class LineView {
        +__init__(line_map)
        +buttons
    }
    
    class LineSelect{
    +__init__(line_map)
    +callback(interaction)
    }
    
    class StationView{
    +__init__(stations)
    }
    
    class StationSelect{
    +__init__(station)
    +callback(interaction)  
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
        +subscribe_to_line(user_id, line_name)
        +unsubscribe_to_line(user_id, line_name)
        +is_user_subscribed(user_id, line_name)
    }

    class Stations {
        +normalize_station(name)
        +REGIONAL_RAIL_STATIONS
    }
    
    class StationAlerts{
    +poll_routes_for_outages()
    +notify_route_alert()
    +get_subscriber_mentions()
    +alerts_slash()
    +set_alert_level_slash()
    +testalert_slash()
    }
    
    class DynamicStationMap {
    +fetch_line_station_map()
     }

    class DiscordPy {
        <<framework>>
        app_commands
        events
    }

    %% Relationships

     
    MyBot --> SeptaApi
    MyBot --> SubscriptionSystem
    MyBot --> DiscordPy
    SeptaApi --> Aiohttp : "uses"
    MyBot --> StationAlerts
    MyBot --> SubscriptionSystem
    MyBot --> SeptaApi
    MyBot --> LineView
    MyBot --> SubscribeLineView
    MyBot --> UnsubscribeLineView
    MyBot --> Stations
    MyBot --> DynamicStationMap
    LineView --> LineSelect
    StationView --> StationSelect
    LineSelect --> StationView  