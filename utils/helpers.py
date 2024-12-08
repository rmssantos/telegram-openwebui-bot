def is_group_chat(message):
    return message.chat.type in ["group", "supergroup"]

