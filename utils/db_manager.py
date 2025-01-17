# utils/db_manager.py

import sqlite3
import os

# Path to your new SQLite DB inside the container
DB_PATH = "/apps/tgbot/bot_data.db"  # We'll mount this file via Docker volume

def init_db():
    """
    Create the database file if it doesn't exist, and create tables.
    """
    conn = sqlite3.connect(DB_PATH)
    with conn:
        # GROUP CHAT LOGS
        conn.execute("""
            CREATE TABLE IF NOT EXISTS group_chat_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT NOT NULL,
                user TEXT,
                text TEXT,
                timestamp TEXT
            );
        """)

        # CHAT HISTORIES (User-Assistant conversations)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chat_histories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT NOT NULL,
                role TEXT,
                content TEXT,
                timestamp TEXT
            );
        """)

        # SUMMARY METADATA
        conn.execute("""
            CREATE TABLE IF NOT EXISTS summary_metadata (
                chat_id TEXT PRIMARY KEY,
                last_summary_time TEXT,
                last_summary_result TEXT,
                last_summary_message_ids TEXT,
                last_warning_message_ids TEXT,
                last_summarized_timestamp TEXT
            );
        """)
    conn.close()

def add_group_message(chat_id, user, text, timestamp):
    conn = sqlite3.connect(DB_PATH)
    with conn:
        conn.execute("""
            INSERT INTO group_chat_logs (chat_id, user, text, timestamp)
            VALUES (?, ?, ?, ?)
        """, (str(chat_id), user, text, timestamp))
    conn.close()

def get_group_messages_in_last_x_hours(chat_id, hours=6, bot_username=None):
    """
    Fetch messages from group_chat_logs in the last `hours` hours,
    exclude bot's own messages and exclude messages starting with '/' 
    (except '/del' if you want).
    """
    conn = sqlite3.connect(DB_PATH)
    cutoff_str = f"-{hours} hours"
    query = """
        SELECT user, text, timestamp 
        FROM group_chat_logs
        WHERE chat_id = ?
          AND timestamp >= DATETIME('now', ?)
        ORDER BY timestamp ASC
    """
    rows = []
    with conn:
        rows = conn.execute(query, (str(chat_id), cutoff_str)).fetchall()
    conn.close()

    filtered = []
    for (u, txt, ts) in rows:
        if bot_username and u and u.lower() == bot_username.lower():
            # Exclude bot messages
            continue
        if txt and txt.strip().startswith('/') and txt.strip().lower() != '/del':
            # Exclude commands except /del
            continue

        filtered.append({
            "user": u,
            "text": txt,
            "timestamp": ts
        })
    return filtered

def add_chat_history_message(chat_id, role, content, timestamp):
    conn = sqlite3.connect(DB_PATH)
    with conn:
        conn.execute("""
            INSERT INTO chat_histories (chat_id, role, content, timestamp)
            VALUES (?, ?, ?, ?)
        """, (str(chat_id), role, content, timestamp))
    conn.close()

def get_chat_history(chat_id):
    """
    Returns all messages from chat_histories (ordered by ID).
    """
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT role, content, timestamp
        FROM chat_histories
        WHERE chat_id = ?
        ORDER BY id ASC
    """
    rows = []
    with conn:
        rows = conn.execute(query, (str(chat_id),)).fetchall()
    conn.close()

    result = []
    for (role, content, ts) in rows:
        result.append({
            "role": role,
            "content": content,
            "timestamp": ts
        })
    return result

def set_summary_metadata(
    chat_id,
    last_summary_time=None,
    last_summary_result=None,
    last_summary_message_ids=None,
    last_warning_message_ids=None,
    last_summarized_timestamp=None
):
    conn = sqlite3.connect(DB_PATH)
    with conn:
        # Check if row exists
        existing = conn.execute("""
            SELECT chat_id FROM summary_metadata WHERE chat_id = ?
        """, (str(chat_id),)).fetchone()

        if existing:
            # Update
            conn.execute("""
                UPDATE summary_metadata
                SET last_summary_time = COALESCE(?, last_summary_time),
                    last_summary_result = COALESCE(?, last_summary_result),
                    last_summary_message_ids = COALESCE(?, last_summary_message_ids),
                    last_warning_message_ids = COALESCE(?, last_warning_message_ids),
                    last_summarized_timestamp = COALESCE(?, last_summarized_timestamp)
                WHERE chat_id = ?
            """, (
                last_summary_time,
                last_summary_result,
                ",".join(map(str, last_summary_message_ids)) if last_summary_message_ids else None,
                ",".join(map(str, last_warning_message_ids)) if last_warning_message_ids else None,
                last_summarized_timestamp,
                str(chat_id)
            ))
        else:
            # Insert
            conn.execute("""
                INSERT INTO summary_metadata (
                    chat_id,
                    last_summary_time,
                    last_summary_result,
                    last_summary_message_ids,
                    last_warning_message_ids,
                    last_summarized_timestamp
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                str(chat_id),
                last_summary_time,
                last_summary_result,
                ",".join(map(str, last_summary_message_ids)) if last_summary_message_ids else None,
                ",".join(map(str, last_warning_message_ids)) if last_warning_message_ids else None,
                last_summarized_timestamp
            ))
    conn.close()

def get_summary_metadata(chat_id):
    """
    Return the summary metadata row as a dict, or {} if none found.
    """
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT chat_id,
               last_summary_time,
               last_summary_result,
               last_summary_message_ids,
               last_warning_message_ids,
               last_summarized_timestamp
        FROM summary_metadata
        WHERE chat_id = ?
    """
    row = None
    with conn:
        row = conn.execute(query, (str(chat_id),)).fetchone()
    conn.close()

    if row is None:
        return {}
    return {
        "last_summary_time": row[1],
        "last_summary_result": row[2],
        "last_summary_message_ids": row[3].split(',') if row[3] else [],
        "last_warning_message_ids": row[4].split(',') if row[4] else [],
        "last_summarized_timestamp": row[5]
    }

