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
    User->>Discord: /subscribe
    Discord->>Bot: Message event

    Bot->>Bot: Fetch list of lines
    Bot->>User: SubscribeLineView (buttons)
    User->>Bot: Select line

    Bot->>SubSys: Save subscription (user_id → line)
    Bot-->>User: "Subscribed to Paoli Line!"

    %% Background notifications
    loop Every 60 seconds
        Bot->>API: get_line_status(subscribed_line)
        API-->>Bot: Status result
        alt If delayed or late
            Bot->>SubSys: notify_line(users, status)
            SubSys->>Discord: Send alert to subscribed users
        end
    end

    %% Fun interactions
    User->>Bot: "good bot" / "spin" / "O I I A I"
    Bot->>Bot: Random compliment OR cat spin logic
    Bot-->>User: Response + cat_spin.gif