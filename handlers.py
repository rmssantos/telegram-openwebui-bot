# handlers.py

import logging
import re  # Importing the re module for regex operations
import math  # For handling long summaries if splitting is needed
from telebot import TeleBot
from config import API_KEY, KB_MAPPINGS
from utils.helpers import is_group_chat
from utils.history import (
    reset_chat_history,
    get_chat_context,
    get_last_24h_messages,
    log_group_message,
    chat_histories
)
from services.openwebui import get_openai_response
from services.summarize import summarize_last_24h
from utils.formatter import sanitize_html, replace_markdown_bold  # Import the formatter functions

logger = logging.getLogger(__name__)
bot = TeleBot(API_KEY)

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(
        message.chat.id,
        "Available Commands:\n"
        "/reset - Reset conversation history\n"
        "/summarize - Summarize the last 24 hours of group chat\n"
        "/chat <message> - Chat with the bot\n"
        "Reply to the bot to continue a conversation."
    )

@bot.message_handler(commands=['chat'])
def chat_command(message):
    user_input = message.text.replace(f"/chat@{bot.get_me().username}", "").strip()
    user_input = user_input.replace("/chat", "").strip()
    try:
        response = get_openai_response(message.chat.id, user_input, chat_histories)
        # Inform the user about applied KBs
        applied_kbs = [kw for kw in KB_MAPPINGS if re.search(r'\b' + re.escape(kw.lower()) + r'\b', user_input.lower())]
        if applied_kbs:
            kb_names = ', '.join(applied_kbs)
            bot.send_message(message.chat.id, f"<b>Applied Knowledge Bases:</b> {kb_names}", parse_mode='HTML')
        # Send the response with HTML formatting
        bot.send_message(message.chat.id, response, parse_mode='HTML')
    except Exception as e:
        logger.error(f"Error in /chat command: {e}")
        bot.send_message(message.chat.id, "An unexpected error occurred while processing your request. Please try again later.")

@bot.message_handler(func=lambda m: m.reply_to_message is not None and m.reply_to_message.from_user.username == bot.get_me().username)
def reply_to_bot(message):
    user_input = message.text.strip()
    try:
        response = get_openai_response(message.chat.id, user_input, chat_histories)
        # Inform the user about applied KBs
        applied_kbs = [kw for kw in KB_MAPPINGS if re.search(r'\b' + re.escape(kw.lower()) + r'\b', user_input.lower())]
        if applied_kbs:
            kb_names = ', '.join(applied_kbs)
            bot.send_message(message.chat.id, f"<b>Applied Knowledge Bases:</b> {kb_names}", parse_mode='HTML')
        # Send the response with HTML formatting
        bot.send_message(message.chat.id, response, parse_mode='HTML')
    except Exception as e:
        logger.error(f"Error handling reply: {e}")
        bot.send_message(message.chat.id, "An unexpected error occurred while processing your request. Please try again later.")

@bot.message_handler(commands=['reset'])
def reset_history_command(message):
    chat_id = message.chat.id
    reset_chat_history(chat_id)
    bot.send_message(chat_id, "Chat history has been reset.")

@bot.message_handler(commands=['summarize'])
def summarize_group_chat_command(message):
    if is_group_chat(message):
        try:
            # Fetch the last 24 hours of messages excluding bot messages and commands
            recent_messages = get_last_24h_messages(message.chat.id, bot_username="Chat Summary")
            # Optionally, include chat context if needed
            chat_context_list = get_chat_context(message.chat.id)
            combined_messages = recent_messages
            if chat_context_list:
                # Add a clear header for the assistant context to improve summarization clarity
                combined_messages += "\n\n--- Assistant Context Start ---\n" + "\n".join(chat_context_list) + "\n--- Assistant Context End ---"

            if not combined_messages.strip():
                bot.send_message(message.chat.id, "No messages in the last 24 hours.")
                logger.debug("Summarization aborted: No messages to process.")
                return

            # Generate the summary using the AI
            summary = summarize_last_24h(message.chat.id)

            # Sanitize the summary to remove any unsupported tags
            summary = sanitize_html(summary)

            # Replace any residual Markdown bold syntax with HTML bold tags and ensure '@' prefix
            summary = replace_markdown_bold(summary)

            # Optionally split the summary if it's too long
            max_length = 4000  # Telegram's limit is 4096
            if len(summary) > max_length:
                parts = math.ceil(len(summary) / max_length)
                for i in range(parts):
                    part = summary[i*max_length:(i+1)*max_length]
                    bot.send_message(message.chat.id, part, parse_mode='HTML')
            else:
                bot.send_message(message.chat.id, summary, parse_mode='HTML')
        except Exception as e:
            logger.error(f"Error summarizing chat: {e}")
            bot.send_message(message.chat.id, "An error occurred while attempting to summarize. Please try again later.")
    else:
        bot.send_message(message.chat.id, "This command is only available in group chats.")

@bot.message_handler(func=lambda message: is_group_chat(message))
def handle_group_message(message):
    log_group_message(message)

