# services/summarize.py

import requests
import logging
import re
from config import OPENWEBUI_BASE_URL, OPENWEBUI_API_KEY, MODEL_NAME, MAX_TOKENS, TEMPERATURE
from utils.history import get_last_24h_messages
from utils.formatter import sanitize_html, replace_markdown_bold

logger = logging.getLogger(__name__)

def summarize_last_24h(chat_id, retries=3, timeout=30):
    """
    Generates a concise summary of the last 24 hours of chat messages using AI.

    Args:
        chat_id (int): The unique identifier for the chat.
        retries (int): Number of retry attempts if the API request fails.
        timeout (int): Timeout duration for the API request.

    Returns:
        str: The AI-generated summary of the chat.
    """
    messages_to_summarize = get_last_24h_messages(chat_id)
    if not messages_to_summarize:
        logger.debug("No messages to summarize.")
        return "No messages in the last 24 hours."

    headers = {
        "Authorization": f"Bearer {OPENWEBUI_API_KEY}",
        "Content-Type": "application/json"
    }

    # Refined prompt
    prompt = (
        "Please provide a concise, numbered summary of the following chat messages. "
        "Use only the following HTML tags for formatting in Telegram: <b>, <strong>, <i>, <em>, and <a>. "
        "Each summary point should start with a number, followed by the username prefixed with '@' in bold, a colon, and a brief summary of the message.\n\n"
        "Example:\n"
        "1. <b>@Username:</b> Greeted everyone in the chat.\n"
        "2. <b>@AnotherUser:</b> Responded with a greeting and asked about @Username's well-being.\n\n"
        f"Chat Messages:\n{messages_to_summarize}"
    )

    data = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": MAX_TOKENS,
        "temperature": TEMPERATURE
    }

    attempt = 0
    while attempt < retries:
        try:
            logger.debug(f"Sending summarization request: {data}")
            response = requests.post(
                f"{OPENWEBUI_BASE_URL}/chat/completions",
                headers=headers,
                json=data,
                timeout=timeout
            )
            logger.debug(f"Summarization response: {response.text}")
            response.raise_for_status()
            response_json = response.json()

            if 'choices' in response_json and response_json['choices']:
                summary = response_json['choices'][0]['message']['content'].strip()

                # Remove code block markers if present
                summary = summary.replace("```html", "").replace("```", "").strip()

                # Remove any unsupported tags just in case
                allowed_tags = ['b', 'strong', 'i', 'em', 'a']
                for tag in ['div', 'span', 'ol', 'li']:
                    summary = re.sub(f"</?{tag}[^>]*>", "", summary, flags=re.IGNORECASE)

                # Replace any remaining Markdown bold syntax with HTML bold tags
                summary = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', summary)

                # Ensure usernames are prefixed with '@' within bold tags
                summary = re.sub(r'<b>([^@][^:]+):</b>', r'<b>@\1:</b>', summary)

                # Ensure summary doesn't exceed Telegram's limit
                if len(summary) > 4000:
                    summary = summary[:4000] + "..."
                return summary
            return "I'm having trouble summarizing the chat history. Please try again later."
        except requests.exceptions.RequestException as e:
            logger.error(f"Summarization request failed (attempt {attempt+1}/{retries}): {e}")
            attempt += 1

    return "There was an error processing the request after multiple attempts. Please try again later."

