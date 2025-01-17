# handlers.py

import logging
import re
import math
import time
from datetime import datetime, timedelta

from telebot import TeleBot
from telebot.apihelper import ApiTelegramException

from config import API_KEY, KB_MAPPINGS, COOLDOWN_MINUTES
from utils.helpers import is_group_chat, is_trusted_user
from utils.history import (
    get_chat_history, 
    get_summary_metadata,
    update_summary_metadata,
    add_to_chat_history,
    log_group_message,
    get_last_summary_message_ids,
    get_last_warning_message_ids,
    get_last_summarized_timestamp,
    get_last_6h_raw_messages,
)
from services.openwebui import get_openai_response
from services.summarize import summarize_categorized
from services.image_analyser import analyze_image
from utils.formatter import sanitize_html, markdown_to_telegram_html
from services.sentiment import analyze_sentiment
from utils.telegram_utils import safe_send_message
from services.sentiment_gauge import get_fear_greed_value, send_resized_fear_greed_image
from services.bing_search_api import query_bing_api  # Our Bing search function

logger = logging.getLogger(__name__)
bot = TeleBot(API_KEY)

# Search cooldown in seconds (e.g. 60)
SEARCH_COOLDOWN_SECONDS = 60
search_cooldowns = {}

# Dictionary to track user cooldowns for sentiment summarization
user_cooldowns = {}


@bot.message_handler(commands=['help'])
def help_command(message):
    text = (
        "Available Commands:\n"
        "/summarize - Summarize the recent group chat\n"
        "/sentiment - Analyse the group sentiment\n"
        "/chat <message> - Chat with the bot\n\n"
        "Reply to the bot to continue a conversation.\n"
        "Use '/chat search: <your query>' to do a Bing search."
    )
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['chat'])
def chat_command(message):
    """
    /chat command handler.
    Usage:
       /chat Hello, how are you?
       /chat search: <search query>
    """
    user_input = message.text.replace(f"/chat@{bot.get_me().username}", "").strip()
    user_input = user_input.replace("/chat", "").strip()

    try:
        # 1) Check if user wants a Bing search
        if user_input.lower().startswith("search:"):
            search_query = user_input[len("search:"):].strip()

            # Enforce search cooldown
            chat_id = message.chat.id
            now = time.time()
            last_search_time = search_cooldowns.get(chat_id, 0)
            elapsed = now - last_search_time

            if elapsed < SEARCH_COOLDOWN_SECONDS:
                wait_sec = int(SEARCH_COOLDOWN_SECONDS - elapsed)
                bot.send_message(
                    chat_id,
                    f"Please wait {wait_sec} second(s) before the next search."
                )
                return
            # Update cooldown
            search_cooldowns[chat_id] = now

            # Execute Bing search
            try:
                results = query_bing_api(query=search_query, count=3, market="en-US")
                if not results:
                    response = "I couldn't find any results for your query. Please try again."
                else:
                    # Format results with HTML
                    response_chunks = []
                    for idx, r in enumerate(results, start=1):
                        chunk = (
                            f"<b>Result {idx}:</b>\n"
                            f"<b>{r['title']}</b>\n"
                            f"<i>{r['snippet']}</i>\n"
                            f"<a href='{r['url']}'>{r['url']}</a>\n\n"
                        )
                        response_chunks.append(chunk)
                    # Combine
                    response = "".join(response_chunks)
                    response += "Use this info for follow-up questions. If asked about these details, refer to the snippet above."
            except Exception as e:
                logger.error(f"Bing Search error: {e}", exc_info=True)
                response = f"Error calling Bing search: {e}"

            # Send to user & store in chat history
            bot.send_message(
                message.chat.id,
                response,
                parse_mode="HTML",
                reply_to_message_id=message.message_id
            )
            snippet_text = "[WEB_SNIPPET]\n" + response
            add_to_chat_history(message.chat.id, "assistant", snippet_text)

        else:
            # 2) Normal GPT-based logic
            add_to_chat_history(message.chat.id, "user", user_input)
            # Retrieve the conversation context from the DB
            context = get_chat_history(message.chat.id)
            response = get_openai_response(message.chat.id, user_input, context)
            add_to_chat_history(message.chat.id, "assistant", response)

            # Convert Markdown-like formatting to Telegram HTML
            formatted_response = markdown_to_telegram_html(response)

            # Optional: Knowledge Base detection
            applied_kbs = [
                kw for kw in KB_MAPPINGS
                if re.search(r'\b' + re.escape(kw.lower()) + r'\b', user_input.lower())
            ]
            if applied_kbs:
                kb_names = ', '.join(applied_kbs)
                bot.send_message(
                    message.chat.id,
                    f"<b>Applied Knowledge Bases:</b> {kb_names}",
                    parse_mode='HTML',
                    reply_to_message_id=message.message_id
                )

            bot.send_message(
                message.chat.id,
                formatted_response,
                parse_mode='HTML',
                reply_to_message_id=message.message_id
            )

    except Exception as e:
        logger.error(f"Error in /chat command: {e}")
        bot.send_message(
            message.chat.id,
            "An unexpected error occurred. Please try again later."
        )


@bot.message_handler(
    func=lambda m: (
        m.reply_to_message is not None
        and m.reply_to_message.from_user.username == bot.get_me().username
    ),
    content_types=['text', 'photo']
)
def reply_to_bot(message):
    """
    When user replies to the bot:
       - If message text starts with "search:", perform a Bing search;
       - Otherwise use normal GPT logic with updated context if replying to a summary;
       - If it's a photo, perform image analysis.
    """
    if message.content_type == 'text' and message.text.strip().lower() == "/del":
        return

    if message.content_type == 'text':
        user_input = message.text.strip()
        try:
            if user_input.lower().startswith("search:"):
                # [Bing search logic remains unchanged]
                chat_id = message.chat.id
                now = time.time()
                last_search_time = search_cooldowns.get(chat_id, 0)
                elapsed = now - last_search_time
                if elapsed < SEARCH_COOLDOWN_SECONDS:
                    wait_sec = int(SEARCH_COOLDOWN_SECONDS - elapsed)
                    bot.send_message(
                        chat_id,
                        f"Please wait {wait_sec} second(s) before the next search."
                    )
                    return
                search_cooldowns[chat_id] = now

                search_query = user_input[len("search:"):].strip()
                try:
                    results = query_bing_api(query=search_query, count=3, market="en-US")
                    if not results:
                        response = "I couldn't find any results. Please try again."
                    else:
                        response_chunks = []
                        for idx, r in enumerate(results, start=1):
                            chunk = (
                                f"<b>Result {idx}:</b>\n"
                                f"<b>{r['title']}</b>\n"
                                f"<i>{r['snippet']}</i>\n"
                                f"<a href='{r['url']}'>{r['url']}</a>\n\n"
                            )
                            response_chunks.append(chunk)
                        response = "".join(response_chunks)
                        response += "Use this info for follow-up questions. If asked, refer to the snippet above."
                except Exception as e:
                    logger.error(f"Bing search error: {e}", exc_info=True)
                    response = f"Error: {e}"

                bot.send_message(
                    message.chat.id,
                    response,
                    parse_mode="HTML",
                    reply_to_message_id=message.message_id
                )
                snippet_text = "[WEB_SNIPPET]\n" + response
                add_to_chat_history(message.chat.id, "assistant", snippet_text)

            else:
                # Normal GPT logic with enhanced context if replying to a summary.
                add_to_chat_history(message.chat.id, "user", user_input)
                # Retrieve the default conversation history:
                context = get_chat_history(message.chat.id)

                # Detect if this reply is to a summary:
                summary_context = ""
                if message.reply_to_message:
                    # Option A: Check if the replied message's ID is in the stored summary IDs.
                    summary_ids = get_last_summary_message_ids(message.chat.id)
                    if message.reply_to_message.message_id in summary_ids:
                        summary_context = "\n[Context Reminder: The previous summary was:] " + message.reply_to_message.text
                    # Option B: Alternatively, check for a content marker (uncomment if using markers):
                    # if "<!--SUMMARY_START-->" in message.reply_to_message.text:
                    #     summary_context = "\n[Context Reminder: The previous summary was:] " + message.reply_to_message.text

                # Append the summary context to the conversation context if it exists:
                if summary_context:
                    context.append({"role": "system", "content": summary_context})

                response = get_openai_response(message.chat.id, user_input, context)
                add_to_chat_history(message.chat.id, "assistant", response)

                formatted_response = markdown_to_telegram_html(response)

                applied_kbs = [
                    kw for kw in KB_MAPPINGS
                    if re.search(r'\b' + re.escape(kw.lower()) + r'\b', user_input.lower())
                ]
                if applied_kbs:
                    kb_names = ', '.join(applied_kbs)
                    bot.send_message(
                        message.chat.id,
                        f"<b>Applied Knowledge Bases:</b> {kb_names}",
                        parse_mode='HTML',
                        reply_to_message_id=message.message_id
                    )

                bot.send_message(
                    message.chat.id,
                    formatted_response,
                    parse_mode='HTML',
                    reply_to_message_id=message.message_id
                )

        except Exception as e:
            logger.error(f"Error handling reply: {e}", exc_info=True)
            bot.send_message(
                message.chat.id,
                "An unexpected error occurred. Please try again later."
            )
    elif message.content_type == 'photo':
        try:
            file_id = message.photo[-1].file_id
            file_info = bot.get_file(file_id)
            image_bytes = bot.download_file(file_info.file_path)
            image_analysis = analyze_image(image_bytes)
            add_to_chat_history(message.chat.id, "user", "[User sent an image]")
            add_to_chat_history(message.chat.id, "assistant", image_analysis)
            bot.send_message(
                message.chat.id,
                text=f"Here's what I see:\n\n{image_analysis}",
                reply_to_message_id=message.message_id
            )
        except Exception as e:
            logger.error(f"Error handling photo reply: {e}", exc_info=True)
            bot.send_message(
                message.chat.id,
                f"An error occurred while analyzing the photo: {e}"
            )


@bot.message_handler(commands=['summarize'])
def summarize_group_chat_command(message):
    logger.debug(f"Summarize command in chat_id={message.chat.id} by user_id={message.from_user.id}")
    if not is_group_chat(message):
        bot.send_message(message.chat.id, "This command is only available in group chats.")
        return

    cid = message.chat.id
    user_id = message.from_user.id

    if not is_trusted_user(bot, cid, user_id):
        last_warning_ids = get_last_warning_message_ids(cid)
        for mid in last_warning_ids:
            try:
                bot.delete_message(cid, mid)
            except ApiTelegramException as exc:
                msg_str = str(exc)
                if "message to delete not found" in msg_str:
                    logger.debug(f"Warning message {mid} not found.")
                else:
                    logger.warning(f"Could not delete old warning message_id={mid}: {exc}")

        warning_msg = bot.send_message(cid, "⚠️ Only trusted (admin/titled) users can request a summary.")
        update_summary_metadata(cid, last_warning_message_ids=[warning_msg.message_id])
        return

    meta = get_summary_metadata(cid)
    last_summary_time_str = meta.get("last_summary_time")
    last_summary_result = meta.get("last_summary_result")
    last_summarized_ts = get_last_summarized_timestamp(cid)
    now = datetime.now()

    if last_summary_time_str:
        last_summary_time = datetime.fromisoformat(last_summary_time_str)
        elapsed = (now - last_summary_time).total_seconds() / 60
        if elapsed < COOLDOWN_MINUTES:
            wait_time = math.ceil(COOLDOWN_MINUTES - elapsed)
            last_warning_ids = get_last_warning_message_ids(cid)
            for mid in last_warning_ids:
                try:
                    bot.delete_message(cid, mid)
                except ApiTelegramException as exc:
                    msg_str = str(exc)
                    if "message to delete not found" in msg_str:
                        logger.debug(f"Warning message {mid} not found.")
                    else:
                        logger.warning(f"Could not delete old warning message_id={mid}: {exc}")

            warning_msg = bot.send_message(
                cid,
                f"⏳ Please wait another {wait_time} minute(s) before requesting another summary."
            )
            update_summary_metadata(cid, last_warning_message_ids=[warning_msg.message_id])
            return

    progress_msg = bot.send_message(cid, "🛠️ Working on your summary, please wait...")

    try:
        recent_raw_messages = get_last_6h_raw_messages(cid, bot_username=bot.get_me().username, hours=6)

        have_newer = True
        if last_summarized_ts:
            have_newer = any(
                datetime.fromisoformat(msg['timestamp']) > last_summarized_ts
                for msg in recent_raw_messages
            )

        if last_summary_result and not have_newer:
            old_summary_ids = get_last_summary_message_ids(cid)
            for mid in old_summary_ids:
                try:
                    bot.delete_message(cid, mid)
                except ApiTelegramException as exc:
                    msg_str = str(exc)
                    if "message to delete not found" in msg_str:
                        logger.debug(f"Old summary message_id={mid} not found.")
                    else:
                        logger.warning(f"Could not delete old summary message_id={mid}: {exc}")

            old_warning_ids = get_last_warning_message_ids(cid)
            for mid in old_warning_ids:
                try:
                    bot.delete_message(cid, mid)
                except ApiTelegramException as exc:
                    msg_str = str(exc)
                    if "message to delete not found" in msg_str:
                        logger.debug(f"Warning message {mid} not found.")
                    else:
                        logger.warning(f"Could not delete old warning message_id={mid}: {exc}")

            bot.send_message(cid, "ℹ️ No new messages since last summary. Here's the cached summary:")
            cached_summary_formatted = markdown_to_telegram_html(last_summary_result)
            msg_ids = safe_send_message(bot, cid, cached_summary_formatted, parse_mode='HTML')

            update_summary_metadata(
                cid,
                last_summary_time=now,
                last_summary_result=last_summary_result,
                last_summary_message_ids=msg_ids,
                last_summarized_timestamp=last_summarized_ts
            )
            return

        old_summary_ids = get_last_summary_message_ids(cid)
        for mid in old_summary_ids:
            try:
                bot.delete_message(cid, mid)
            except ApiTelegramException as exc:
                msg_str = str(exc)
                if "message to delete not found" in msg_str:
                    logger.debug(f"Summary message {mid} not found.")
                else:
                    logger.warning(f"Could not delete old summary message_id={mid}: {exc}")

        old_warning_ids = get_last_warning_message_ids(cid)
        for mid in old_warning_ids:
            try:
                bot.delete_message(cid, mid)
            except ApiTelegramException as exc:
                msg_str = str(exc)
                if "message to delete not found" in msg_str:
                    logger.debug(f"Warning msg {mid} missing.")
                else:
                    logger.warning(f"Could not delete old warning message_id={mid}: {exc}")

        summary = summarize_categorized(cid, bot_username=bot.get_me().username)
        if not summary or "An error occurred" in summary:
            try:
                bot.delete_message(cid, progress_msg.message_id)
            except:
                pass
            bot.send_message(cid, "❌ Sorry, I couldn't generate a summary at this time.")
        else:
            try:
                bot.delete_message(cid, progress_msg.message_id)
            except:
                pass

            summary_formatted = markdown_to_telegram_html(summary)
            new_message_ids = safe_send_message(bot, cid, summary_formatted, parse_mode='HTML')

            if recent_raw_messages:
                newest_msg_ts = max(datetime.fromisoformat(msg['timestamp']) for msg in recent_raw_messages)
            else:
                newest_msg_ts = now

            update_summary_metadata(
                cid,
                last_summary_time=now,
                last_summary_result=summary,
                last_summary_message_ids=new_message_ids,
                last_summarized_timestamp=newest_msg_ts
            )

    except Exception as e:
        logger.error(f"Error summarizing chat: {e}")
        bot.send_message(cid, "❌ An error occurred while attempting to summarize.")
    finally:
        try:
            bot.delete_message(cid, progress_msg.message_id)
        except:
            pass


@bot.message_handler(commands=['sentiment'])
def sentiment_command(message):
    logger.debug(f"Sentiment command in chat_id={message.chat.id}, user_id={message.from_user.id}")
    cid = message.chat.id
    user_id = message.from_user.id
    current_time = datetime.now()

    if not is_group_chat(message):
        bot.send_message(cid, "This command is only available in group chats.")
        return

    if not is_trusted_user(bot, cid, user_id):
        warning_msg = bot.send_message(cid, "⚠️ Only trusted (admin/titled) users can request sentiment analysis.")
        update_summary_metadata(cid, last_warning_message_ids=[warning_msg.message_id])
        return

    cooldown_end = user_cooldowns.get(user_id)
    if cooldown_end and current_time < cooldown_end:
        remaining_time = (cooldown_end - current_time).total_seconds() / 60
        wait_time = math.ceil(remaining_time)
        bot.send_message(cid, f"⏳ Please wait {wait_time} minute(s) before requesting sentiment analysis again.")
        return

    user_cooldowns[user_id] = current_time + timedelta(minutes=COOLDOWN_MINUTES)

    progress_msg = bot.send_message(cid, "🛠️ Analyzing sentiment, please wait...")

    try:
        recent_raw_messages = get_last_6h_raw_messages(cid, bot_username=bot.get_me().username)
        if not recent_raw_messages:
            bot.send_message(cid, "No messages found for sentiment analysis.")
            return

        sentiment_result = analyze_sentiment(recent_raw_messages)
        sentiment_result_formatted = markdown_to_telegram_html(sentiment_result)

        bot.send_message(cid, sentiment_result_formatted, parse_mode='HTML')

        global_value, global_class = get_fear_greed_value()
        send_resized_fear_greed_image(bot, cid, global_value, global_class, width=250)

    except Exception as e:
        logger.error(f"Error analyzing sentiment in chat_id={cid}: {e}", exc_info=True)
        bot.send_message(cid, "❌ An error occurred while analyzing sentiment.")
    finally:
        try:
            bot.delete_message(cid, progress_msg.message_id)
        except Exception as ex:
            logger.warning(f"Failed to delete progress message: {ex}")


@bot.message_handler(func=lambda m: is_group_chat(m))
def handle_group_message(message):
    logger.debug(
        f"Group msg from {message.from_user.username} in {message.chat.id}: {message.text}"
    )
    log_group_message(message)