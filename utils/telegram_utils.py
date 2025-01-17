# utils/telegram_utils.py

def safe_send_message(bot, chat_id, text, parse_mode="HTML", chunk_size=4000):
    """
    Sends a message in multiple parts if it exceeds the chunk_size limit.
    """
    if len(text) <= chunk_size:
        # <= chunk_size means 1 message only
        msg = bot.send_message(chat_id, text, parse_mode=parse_mode)
        return [msg.message_id]

    message_ids = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end]
        msg = bot.send_message(chat_id, chunk, parse_mode=parse_mode)
        message_ids.append(msg.message_id)
        start = end
    return message_ids

