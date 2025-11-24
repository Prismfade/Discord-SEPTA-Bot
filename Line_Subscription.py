import asyncio

# Dictionary to keep track of subscriptions
# {user_id: set([line_names])}
user_line_subscriptions = {}

async def subscribe_to_line(user_id, line_name):
    subs = user_line_subscriptions.get(user_id, [])
    if line_name not in subs:
        subs.append(line_name)
        user_line_subscriptions[user_id] = subs
        return f"Subscribed to {line_name}"
    return f"Already subscribed to {line_name}"

async def unsubscribe_to_line(user_id, line_name):
    subs = user_line_subscriptions.get(user_id, [])
    if line_name in subs:
        subs.remove(line_name)
        user_line_subscriptions[user_id] = subs
        return f"Unsubscribed from {line_name}"
    return f"Not subscribed to {line_name}"

async def get_user_subscriptions(user_id):
    return user_line_subscriptions.get(user_id, [])

async def notify_line(bot, line_name, text):
    # Placeholder: notify all users subscribed to a line
    count = 0
    for user_id, subs in user_line_subscriptions.items():
        if line_name in subs:
            user = await bot.fetch_user(user_id)
            if user:
                try:
                    await user.send(f"Notification for **{line_name}**: {text}")
                    count += 1
                except:
                    pass
    return count