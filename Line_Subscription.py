import asyncio

# Dictionary to keep track of subscriptions
# {user_id: set([line_names])}
user_line_subscriptions = {}


async def subscribe_to_line(user_id, line_name):
    # Get current subscriptions or create a new set
    subs = user_line_subscriptions.get(user_id, set())
    if line_name not in subs:
        subs.add(line_name)
        user_line_subscriptions[user_id] = subs
        return f"Subscribed {user_id} to {line_name}"
    return f"Already subscribed {user_id} to {line_name}"


async def unsubscribe_to_line(user_id, line_name):
    subs = user_line_subscriptions.get(user_id, set())
    if line_name in subs:
        subs.remove(line_name)
        # If the subscriptions are empty, remove user from dict (optional)
        if subs:
            user_line_subscriptions[user_id] = subs
        else:
            user_line_subscriptions.pop(user_id)
        return f"Unsubscribed {user_id} from {line_name}"
    return f"{user_id} was not subscribed to {line_name}"


async def get_user_subscriptions(user_id):
    # Return the set (as a list for display) of all lines the user is subscribed to
    return list(user_line_subscriptions.get(user_id, set()))


async def is_user_subscribed(user_id, line_name):
    # Utility: check if user is subscribed to a line
    return line_name in user_line_subscriptions.get(user_id, set())

async def notify_line(bot, line_name, text):
    # Placeholder: notify all users subscribed to a line
    count = 0
    for user_id, subs in user_line_subscriptions.items():
        if line_name in subs:
            user = await bot.fetch_user(user_id)
            if user:
                try:
                    await user.send(f"Notification for {line_name}: {text}")
                    count += 1
                except:
                    pass
    return count
