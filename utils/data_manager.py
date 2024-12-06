import json
import os
import logging

logger = logging.getLogger(__name__)

DATA_FILE = "data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        logger.debug(f"No data file found. Creating a new one at {DATA_FILE}")
        return {"chat_histories": {}, "group_chat_logs": {}}

    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if "chat_histories" not in data:
                data["chat_histories"] = {}
            if "group_chat_logs" not in data:
                data["group_chat_logs"] = {}
            return data
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error loading data file: {e}")
        return {"chat_histories": {}, "group_chat_logs": {}}

def save_data(data):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except IOError as e:
        logger.error(f"Error saving data to file: {e}")
