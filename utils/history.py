from datetime import datetime, timedelta
from utils.data_manager import load_data, save_data
from config import HISTORY_LENGTH
import logging
import time

logger = logging.getLogger(__name__)

_data = load_data()
chat_histories = _data.get("chat_histories", {})
group_chat_logs = _data.get("group_chat_logs", {})

# Control variables for batched persistence
_last_persist_time = time.time()
_persist_interval = 30  # seconds between forced persists
_changes_since_last_persist = 0
_max_changes_before_persist = 5  # persist after this many changes

# Prune settings
MAX_GROUP_MESSAGES = 1000  # Keep at most 1000 recent group messages

def persist_data(force=False):
    global _last_persist_time, _changes_since_last_persist
    if (force or 
        _changes_since_last_persist >= _max_changes_before_persist or 
        (time.time() - _last_persist_time) > _persist_interval):
        data_to_save = {
            "chat_histories": chat_histories,
            "group_chat_logs": group_chat_logs
        }
        save_data(data_to_save)
        _last_persist_time = time.time()
        _changes_since_last_persist = 0

def add_to_chat_history(chat_id, role, content, max_length=HISTORY_LENGTH):
    cid = str(chat_id)
    if cid not in chat_histories:
        chat_histories[cid] = []
    chat_histories[cid].append({"role": role, "content": content})
    if len(chat_histories[cid]) > max_length:
        chat_histories[cid] = chat_histories[cid][-max_length:]
    global _changes_since_last_persist
    _changes_since_last_persist += 1
    persist_data()

def log_group_message(message):
    cid = str(message.chat.id)
    if cid not in group_chat_logs:
        group_chat_logs[cid] = []
    group_chat_logs[cid].append({
        "user": message.from_user.username or message.from_user.first_name,
        "text": message.text,
        "timestamp": datetime.now().isoformat()
    })
    # Prune old messages if too large
    if len(group_chat_logs[cid]) > MAX_GROUP_MESSAGES:
        group_chat_logs[cid] = group_chat_logs[cid][-MAX_GROUP_MESSAGES:]
    global _changes_since_last_persist
    _changes_since_last_persist += 1
    persist_data()

def get_last_24h_messages(chat_id, bot_username="Chat Summary"):
    """
    Retrieves the last 24 hours of messages from the specified chat, excluding messages
    from the bot itself and any bot commands.

    Args:
        chat_id (int): The unique identifier for the chat.
        bot_username (str): The username of the bot to exclude its messages. Defaults to "Chat Summary".

    Returns:
        str: A formatted string of recent messages suitable for summarization.
    """
    cid = str(chat_id)
    if cid not in group_chat_logs:
        return ""

    now = datetime.now()
    cutoff_time = now - timedelta(hours=24)
    recent_messages = []

    for msg in group_chat_logs[cid]:
        try:
            ts = datetime.fromisoformat(msg['timestamp'])
        except ValueError:
            # If timestamp format is incorrect, skip the message
            continue

        if ts >= cutoff_time:
            # Exclude messages sent by the bot itself
            if msg['user'].lower() == bot_username.lower():
                continue

            # Exclude messages that are bot commands (start with '/')
            if msg['text'].strip().startswith('/'):
                continue

            # Optionally, exclude messages that are empty or contain only whitespace
            if not msg['text'].strip():
                continue

            # Format the message with '@' prefix for usernames
            # Ensure that the username doesn't already start with '@'
            username = msg['user']
            if not username.startswith('@'):
                username = f"@{username}"

            formatted_message = f"{username}: {msg['text'].strip()}"
            recent_messages.append(formatted_message)

    return "\n".join(recent_messages) if recent_messages else ""

def get_chat_context(chat_id):
    cid = str(chat_id)
    return [f"{msg['role']}: {msg['content']}" for msg in chat_histories.get(cid, [])]

def reset_chat_history(chat_id):
    cid = str(chat_id)
    chat_histories[cid] = []
    # Force persist since this is a user-triggered action
    persist_data(force=True)

