# utils/history.py

import logging
import time
from datetime import datetime
from config import HISTORY_LENGTH, ROTATION_THRESHOLD_HOURS, SUMMARIZATION_HOURS

# Import your new DB manager functions
from utils.db_manager import (
    init_db,
    add_group_message,
    get_group_messages_in_last_x_hours,
    add_chat_history_message,
    get_chat_history,
    set_summary_metadata,
    get_summary_metadata
)

logger = logging.getLogger(__name__)

# Placeholder for persist rotation structure.
_last_persist_time = time.time()
_persist_interval = 30  # seconds
_changes_since_last_persist = 0
_max_changes_before_persist = 5

# Initialize the database (creates tables if not present)
init_db()

def persist_data(force=False):
    """
    In SQLite, each write is immediately committed.
    We'll keep this function for compatibility with your current code.
    """
    global _last_persist_time, _changes_since_last_persist
    now = time.time()
    if (force or
        _changes_since_last_persist >= _max_changes_before_persist or
        (now - _last_persist_time) > _persist_interval):
        logger.debug("SQLite data is automatically persisted; no explicit save needed.")
        _last_persist_time = now
        _changes_since_last_persist = 0

def add_to_chat_history(chat_id, role, content, max_length=HISTORY_LENGTH):
    """
    Inserts a new message into the chat_histories table.
    """
    timestamp = datetime.now().isoformat()
    add_chat_history_message(chat_id, role, content, timestamp)
    global _changes_since_last_persist
    _changes_since_last_persist += 1
    persist_data()
    # Note: if you want to limit the number of messages, you can add deletion logic here.

def log_group_message(message):
    """
    Inserts a group message into the group_chat_logs table.
    """
    cid = message.chat.id
    user = message.from_user.username or message.from_user.first_name
    text = message.text
    timestamp = datetime.now().isoformat()
    add_group_message(cid, user, text, timestamp)
    global _changes_since_last_persist
    _changes_since_last_persist += 1
    persist_data()
    logger.debug(f"Logged message in cid={cid}, user={user}, text={text}")

def get_last_6h_raw_messages(chat_id, bot_username="Chat Summary", hours=SUMMARIZATION_HOURS):
    """
    Returns messages from the last X hours from the DB.
    """
    return get_group_messages_in_last_x_hours(chat_id, hours=hours, bot_username=bot_username)

def update_summary_metadata(
    chat_id,
    last_summary_time=None,
    last_summary_result=None,
    last_summary_message_ids=None,
    last_warning_message_ids=None,
    last_summarized_timestamp=None
):
    set_summary_metadata(
        chat_id,
        last_summary_time=last_summary_time.isoformat() if last_summary_time else None,
        last_summary_result=last_summary_result,
        last_summary_message_ids=last_summary_message_ids,
        last_warning_message_ids=last_warning_message_ids,
        last_summarized_timestamp=last_summarized_timestamp.isoformat() if last_summarized_timestamp else None
    )
    global _changes_since_last_persist
    _changes_since_last_persist += 1
    persist_data()

def get_last_summary_message_ids(chat_id):
    meta = get_summary_metadata(chat_id)
    return meta.get("last_summary_message_ids", [])

def get_last_warning_message_ids(chat_id):
    meta = get_summary_metadata(chat_id)
    return meta.get("last_warning_message_ids", [])

def get_last_summarized_timestamp(chat_id):
    meta = get_summary_metadata(chat_id)
    ts_str = meta.get("last_summarized_timestamp")
    if ts_str:
        return datetime.fromisoformat(ts_str)
    return None

