# services/openwebui.py

import requests
import logging
import re
from config import OPENWEBUI_BASE_URL, OPENWEBUI_API_KEY, MODEL_NAME, MAX_TOKENS, TEMPERATURE, KB_MAPPINGS
from utils.history import add_to_chat_history, chat_histories

logger = logging.getLogger(__name__)

def get_openai_response(chat_id, user_input, chat_histories_dict, retries=3, timeout=30):
    headers = {
        "Authorization": f"Bearer {OPENWEBUI_API_KEY}",
        "Content-Type": "application/json"
    }

    add_to_chat_history(chat_id, "user", user_input)
    data = {
        "model": MODEL_NAME,
        "messages": chat_histories_dict[str(chat_id)],
        "max_tokens": MAX_TOKENS,
        "temperature": TEMPERATURE
    }

    # Detect keywords and apply corresponding KBs using whole word matching
    applied_kbs = set()
    for keyword, kb_id in KB_MAPPINGS.items():
        # Compile regex pattern for whole word matching, case-insensitive
        pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
        if re.search(pattern, user_input.lower()):
            if "files" not in data:
                data["files"] = []
            # Avoid adding the same KB multiple times
            if kb_id not in {file['id'] for file in data["files"]}:
                data["files"].append({"type": "collection", "id": kb_id})
                applied_kbs.add(keyword)

    if applied_kbs:
        logger.debug(f"Applied Knowledge Bases based on keywords: {', '.join(applied_kbs)}")

    attempt = 0
    while attempt < retries:
        try:
            logger.debug(f"Sending request to OpenWebUI: {data}")
            response = requests.post(
                f"{OPENWEBUI_BASE_URL}/chat/completions",
                headers=headers,
                json=data,
                timeout=timeout
            )
            logger.debug(f"OpenWebUI response: {response.text}")
            response.raise_for_status()
            response_json = response.json()
            if 'choices' in response_json and response_json['choices']:
                bot_response = response_json['choices'][0]['message']['content'].strip()
                add_to_chat_history(chat_id, "assistant", bot_response)
                return bot_response
            return "I'm having trouble getting a response right now. Please try again later."
        except requests.exceptions.RequestException as e:
            logger.error(f"OpenWebUI request failed (attempt {attempt+1}/{retries}): {e}")
            attempt += 1
    return "There was an error processing your request after multiple attempts. Please try again later."

