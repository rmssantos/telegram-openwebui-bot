import requests
import logging
from config import OPENWEBUI_BASE_URL, OPENWEBUI_API_KEY, MODEL_NAME, MAX_TOKENS, TEMPERATURE, KNOWLEDGE_BASE_ID, KEYWORD
from utils.history import add_to_chat_history, chat_histories

logger = logging.getLogger(__name__)

def get_openai_response(chat_id, user_input, chat_histories_dict):
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

    # Check if the keyword is present and the knowledge base is set
    if KEYWORD.lower() in user_input.lower():
        if KNOWLEDGE_BASE_ID:
            data["files"] = [{"type": "collection", "id": KNOWLEDGE_BASE_ID}]
        else:
            logger.warning("Keyword detected, but KNOWLEDGE_BASE_ID is not set. Skipping knowledge base attachment.")
            # Optionally, return a special message or just continue without files.

    try:
        logger.debug(f"Sending request to OpenWebUI: {data}")
        response = requests.post(
            f"{OPENWEBUI_BASE_URL}/chat/completions",
            headers=headers,
            json=data
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
        logger.error(f"OpenWebUI request failed: {e}")
        return "There was an error processing your request. Please try again later."
