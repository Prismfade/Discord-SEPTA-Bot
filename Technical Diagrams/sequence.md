## Sequence Diagram — SEPTA Bot (Current Functionality)

```mermaid
sequenceDiagram
    participant User
    participant Discord as Discord Server
    participant Bot as MyBot
    participant API as SEPTA API
    participant SubSys as Subscription System

    %% User triggers a slash command
    User->>Discord: /next train
    Discord->>Bot: Slash Command Event

    Bot->>Bot: Parse stations\n(normalize_station)
    Bot->>API: get_next_train(origin, dest)
    API-->>Bot: Train data (JSON)
    Bot-->>Discord: "Next train arrives in X minutes"

    %% User checks line status
    User->>Discord: /check line status
    Discord->>Bot: Message event

    Bot->>User: "Which line?"
    User->>Bot: "Paoli"
    Bot->>API: get_line_status("Paoli")
    API-->>Bot: Line status (delays, ETA)
    Bot-->>Discord: Formatted status message

    %% User subscribes to a line
    User->>Discord: /subscribemenu
    Discord->>Bot: Slash Command Event
    Bot->>API: fetch_line_station_map()
    Bot-->>Discord: Show SubscribeLineView (dropdown)
    User->>Bot: Select line
    Bot->>SubSys: subscribe_to_line(user, line)
    Bot-->>Discord: "Subscribed!"
    

    %% Background notifications
    loop Every 90 seconds(StationAlerts Cog)
    
        Bot->>API: fetch_route_alerts()
        API-->>Alerts: detect outage/delay
            Alerts->>SubSys: get subscribers
            Alerts->>Discord: Send outage embed
            SubSys->>Discord: DM subscribers
    end


    User->>Discord: /menu
    Discord->>Bot: Slash command event
    Bot->>API: fetch_line_station_map()
    API-->>Bot: line_map
    Bot-->>Discord: Send LineView (dropdown)
    User->>UI: Select line
    UI->>Bot: LineSelect.callback()
    Bot->>API: get_line_status(line)
    API-->>Bot: status JSON
    Bot-->>Discord: Send StationView (dropdown)
    User->>UI: Select station
    UI->>Bot: StationSelect.callback()
    Bot->>API: get_station_arrivals(station)
    API-->>Bot: arrival JSON
    Bot-->>Discord: Full arrival info
    
    
    %% Fun interactions
    User->>Discord: "good bot" / "spin" / "O I I A I"
    Discord->>Bot: on_message event
    Bot->>Bot: Random compliment OR cat spin logic
    Bot-->>Discord: Response + cat_spin.gif