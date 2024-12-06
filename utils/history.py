from datetime import datetime, timedelta
from utils.data_manager import load_data, save_data
from config import HISTORY_LENGTH
import logging

logger = logging.getLogger(__name__)

# Load data at import
_data = load_data()
chat_histories = _data.get("chat_histories", {})
group_chat_logs = _data.get("group_chat_logs", {})

def persist_data():
    global chat_histories, group_chat_logs
    data_to_save = {
        "chat_histories": chat_histories,
        "group_chat_logs": group_chat_logs
    }
    save_data(data_to_save)

def add_to_chat_history(chat_id, role, content, max_length=HISTORY_LENGTH):
    cid = str(chat_id)
    if cid not in chat_histories:
        chat_histories[cid] = []
    chat_histories[cid].append({"role": role, "content": content})
    if len(chat_histories[cid]) > max_length:
        chat_histories[cid] = chat_histories[cid][-max_length:]
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
    persist_data()

def get_last_24h_messages(chat_id):
    cid = str(chat_id)
    if cid not in group_chat_logs:
        return ""
    now = datetime.now()
    cutoff_time = now - timedelta(hours=24)
    recent_messages = []
    for msg in group_chat_logs[cid]:
        ts = datetime.fromisoformat(msg['timestamp'])
        if ts >= cutoff_time:
            recent_messages.append(f"{msg['user']}: {msg['text']}")
    return "\n".join(recent_messages) if recent_messages else ""

def get_chat_context(chat_id):
    cid = str(chat_id)
    return [f"{msg['role']}: {msg['content']}" for msg in chat_histories.get(cid, [])]

def reset_chat_history(chat_id):
    cid = str(chat_id)
    chat_histories[cid] = []
    persist_data()
