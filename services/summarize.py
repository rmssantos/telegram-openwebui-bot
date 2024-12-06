import requests
import logging
from config import OPENWEBUI_BASE_URL, OPENWEBUI_API_KEY, MODEL_NAME, MAX_TOKENS, TEMPERATURE
from utils.history import get_last_24h_messages

logger = logging.getLogger(__name__)

def summarize_last_24h(chat_id, messages_to_summarize=None):
    if messages_to_summarize is None:
        messages_to_summarize = get_last_24h_messages(chat_id)

    messages = messages_to_summarize
    if not messages.strip():
        logger.debug("No messages to summarize.")
        return "No messages in the last 24 hours."

    headers = {
        "Authorization": f"Bearer {OPENWEBUI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": f"Provide a structured, numbered summary of the following chat messages:\n{messages}"
            }
        ],
        "max_tokens": MAX_TOKENS,
        "temperature": TEMPERATURE
    }

    try:
        logger.debug(f"Sending summarization request: {data}")
        response = requests.post(
            f"{OPENWEBUI_BASE_URL}/chat/completions",
            headers=headers,
            json=data
        )
        logger.debug(f"Summarization response: {response.text}")
        response.raise_for_status()
        response_json = response.json()

        if 'choices' in response_json and response_json['choices']:
            summary = response_json['choices'][0]['message']['content'].strip()
            return summary
        return "I'm having trouble summarizing the chat history. Please try again later."
    except requests.exceptions.RequestException as e:
        logger.error(f"Summarization request failed: {e}")
        return "There was an error processing the request. Please try again later."
