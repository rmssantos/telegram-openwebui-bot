import logging
from telebot import TeleBot
from config import API_KEY
from utils.helpers import is_group_chat
from utils.history import reset_chat_history, get_chat_context, get_last_24h_messages, log_group_message, chat_histories
from services.openwebui import get_openai_response
from services.summarize import summarize_last_24h

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
        "Reply to a bot message to continue the conversation."
    )

@bot.message_handler(commands=['chat'])
def chat_command(message):
    user_input = message.text.replace(f"/chat@{bot.get_me().username}", "").strip()
    user_input = user_input.replace("/chat", "").strip()
    try:
        response = get_openai_response(message.chat.id, user_input, chat_histories)
        bot.send_message(message.chat.id, response)
    except Exception as e:
        logger.error(f"Error in /chat command: {e}")
        bot.send_message(message.chat.id, f"Error: {e}")

@bot.message_handler(func=lambda m: m.reply_to_message is not None and m.reply_to_message.from_user.username == bot.get_me().username)
def reply_to_bot(message):
    user_input = message.text.strip()
    try:
        response = get_openai_response(message.chat.id, user_input, chat_histories)
        bot.send_message(message.chat.id, response)
    except Exception as e:
        logger.error(f"Error handling reply: {e}")
        bot.send_message(message.chat.id, f"Error: {e}")

@bot.message_handler(commands=['reset'])
def reset_history_command(message):
    chat_id = message.chat.id
    reset_chat_history(chat_id)
    bot.send_message(chat_id, "Chat history has been reset.")

@bot.message_handler(commands=['summarize'])
def summarize_group_chat_command(message):
    if is_group_chat(message):
        try:
            recent_messages = get_last_24h_messages(message.chat.id)
            chat_context_list = get_chat_context(message.chat.id)

            combined_messages = recent_messages
            if chat_context_list:
                combined_messages += "\n" + "\n".join(chat_context_list)

            if not combined_messages.strip():
                bot.send_message(message.chat.id, "No messages in the last 24 hours.")
                logger.debug("Summarization aborted: No messages to process.")
                return

            summary = summarize_last_24h(message.chat.id, combined_messages)
            bot.send_message(message.chat.id, summary)
        except Exception as e:
            logger.error(f"Error summarizing chat: {e}")
            bot.send_message(message.chat.id, f"Error: {e}")
    else:
        bot.send_message(message.chat.id, "This command is only available in group chats.")

@bot.message_handler(func=lambda message: is_group_chat(message))
def handle_group_message(message):
    log_group_message(message)
