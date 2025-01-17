# services/openwebui.py

import requests
import logging
from config import (
    OPENWEBUI_BASE_URL,
    OPENWEBUI_API_KEY,
    MODEL_NAME,
    MAX_TOKENS,
    TEMPERATURE
)
from utils.history import add_to_chat_history

logger = logging.getLogger(__name__)

def get_openai_response(chat_id, user_input, chat_history_input, retries=3, timeout=30):
    """
    Calls the local/remote LLM for a response.
    A special system message is prepended to instruct the LLM.
    
    The parameter chat_history_input is expected to be a list of message dicts,
    each with keys "role" and "content". (If a dict is passed instead, we try to extract
    the conversation for this chat_id.)
    """
    # (In the handlers, user's message has already been added to the chat history.)
    system_message = {
        "role": "system",
        "content": (
            "You are a helpful AI assistant. If there is any [WEB_SNIPPET] in the messages, "
            "and the user asks something that snippet can answer, you MUST reference and use "
            "that snippet data. Do not ignore or contradict it."
        )
    }

    # If chat_history_input is a list, use it directly.
    if isinstance(chat_history_input, list):
        conversation = chat_history_input
    elif isinstance(chat_history_input, dict):
        conversation = chat_history_input.get(str(chat_id), [])
    else:
        conversation = []

    # Build the final list of messages.
    final_messages = [system_message]
    for msg in conversation:
        role = msg.get("role")
        content = msg.get("content")
        final_messages.append({"role": role, "content": content})

    data = {
        "model": MODEL_NAME,
        "messages": final_messages,
        "max_tokens": MAX_TOKENS,
        "temperature": TEMPERATURE
    }

    headers = {
        "Authorization": f"Bearer {OPENWEBUI_API_KEY}",
        "Content-Type": "application/json"
    }
    attempt = 0
    while attempt < retries:
        try:
            logger.debug(f"Sending request to OpenWebUI (text): {data}")
            response = requests.post(
                f"{OPENWEBUI_BASE_URL}/chat/completions",
                headers=headers,
                json=data,
                timeout=timeout
            )
            logger.debug(f"OpenWebUI (text) response: {response.text}")
            response.raise_for_status()
            response_json = response.json()

            if 'choices' in response_json and response_json['choices']:
                bot_response = response_json['choices'][0]['message']['content'].strip()
                add_to_chat_history(chat_id, "assistant", bot_response)
                return bot_response
            else:
                return (
                    "I'm having trouble getting a response right now. "
                    "Please try again later."
                )

        except requests.exceptions.RequestException as e:
            logger.error(
                f"OpenWebUI (text) request failed (attempt {attempt+1}/{retries}): {e}"
            )
            attempt += 1

    return (
        "There was an error processing your request after multiple attempts. "
        "Please try again later."
    )

