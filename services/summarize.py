# services/summarize.py

import logging
from config import SUMMARIZATION_HOURS, BASE_CHUNK_SIZE
from utils.history import get_last_6h_raw_messages
from services.chunk_processor import process_chunks, create_session_with_retry, call_openwebui
from utils.formatter import add_emoticons_to_summary  # Import the new emoticon enhancer

logger = logging.getLogger(__name__)

# 1) PARTIAL SUMMARIES
def partial_summary_prompt(chunk, index, total):
    return (
        f"This is chunk {index}/{total} of a large group chat.\n"
        "Summarize it in 2 bullet points (very concise):\n\n"
        f"{chunk}\n"
    )

def partial_combine_fn(partial_summaries):
    return "\n---\n".join(partial_summaries)

# 2) FINAL MERGE PROMPT
def final_merge_prompt(partials_text):
    return (
        "You have multiple short partial summaries below.\n"
        "Combine them into ONE final summary, strictly under 2500 characters.\n"
        "Use at most 3 bullet points, plus 1 concluding sentence.\n\n"
        f"PARTIAL SUMMARIES:\n{partials_text}\n\n"
        "Now produce the final short summary (<2500 chars)."
    )

def summarize_categorized(chat_id, bot_username="Chat Summary"):
    """
    Returns a final short summary (<2500 chars) from the last X hours of chat,
    enhanced with emoticons.
    """
    raw_messages = get_last_6h_raw_messages(chat_id, bot_username=bot_username, hours=SUMMARIZATION_HOURS)
    if not raw_messages:
        return "No messages in the last 6 hours."

    text_to_summarize = "\n".join(
        f"@{m['user']}: {m['text'].strip()}" for m in raw_messages
    )

    # 1) Partial summaries
    partial_summaries_text = process_chunks(
        text_to_summarize,
        prompt_generator_fn=partial_summary_prompt,
        combine_fn=partial_combine_fn,
        chunk_size=BASE_CHUNK_SIZE,
        parallel=True,
        max_workers=2,
        chunk_timeout=30
    )

    # 2) Final unify
    prompt = final_merge_prompt(partial_summaries_text)
    session = create_session_with_retry()
    final_summary = call_openwebui(prompt, session=session, timeout=60)

    if len(final_summary) > 2500:
        final_summary = final_summary[:2490] + "..."

    # 3) Enhance with emoticons
    final_summary_with_emoticons = add_emoticons_to_summary(final_summary)

    return final_summary_with_emoticons

