# utils/helpers.py

import logging
import time

logger = logging.getLogger(__name__)

def is_group_chat(message):
    """
    Determines if a message is from a group or supergroup chat.
    
    Args:
        message (telebot.types.Message): The incoming Telegram message.
    
    Returns:
        bool: True if the message is from a group or supergroup chat, False otherwise.
    """
    chat_type = message.chat.type
    logger.debug(f"is_group_chat check: chat_type={chat_type}")
    return chat_type in ["group", "supergroup"]

def is_trusted_user(bot_instance, chat_id, user_id, attempt=1, max_attempts=3):
    """
    Determine if a user is trusted (e.g., admin or has a specific role/title).
    
    Args:
        bot_instance (TeleBot): The instance of the TeleBot.
        chat_id (int): The ID of the chat.
        user_id (int): The ID of the user.
        attempt (int, optional): Current attempt number. Defaults to 1.
        max_attempts (int, optional): Maximum number of attempts. Defaults to 3.
    
    Returns:
        bool: True if the user is trusted, False otherwise.
    """
    try:
        member = bot_instance.get_chat_member(chat_id, user_id)
        if member.status in ["administrator", "creator"]:
            return True
        if member.custom_title and member.custom_title.strip():
            return True
        return False
    except Exception as e:
        logger.error(f"Error checking user role (attempt {attempt}): {e}")
        if attempt < max_attempts:
            time.sleep(1)
            return is_trusted_user(bot_instance, chat_id, user_id, attempt+1, max_attempts)
        return False

