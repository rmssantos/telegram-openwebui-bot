# services/sentiment.py

import logging
from services.chunk_processor import process_chunks, create_session_with_retry, call_openwebui
from config import BASE_CHUNK_SIZE

logger = logging.getLogger(__name__)

###############################################################################
# 1) PARTIAL SENTIMENT (chunk-based)
###############################################################################

def partial_sentiment_prompt(chunk, index, total):
    """
    Prompt to analyze a chunk of messages for sentiment.
    We'll keep it detailed, because we do a final merge for brevity.
    """
    return (
        f"This is chunk {index}/{total} of a crypto-related group chat.\n\n"
        f"{chunk}\n\n"
        "Analyze the sentiment and produce a short summary with:\n"
        "- Overall Hodlers chat group Sentiment (Bullish 🚀, Bearish 🛑, or Neutral 🤔)\n"
        "- Percentages of Positive, Neutral, and Negative\n"
        "- A few key topics or observations."
    )

def partial_sentiment_combine_fn(partial_results):
    """
    Joins partial chunk results into one text. We'll do a 2nd pass
    to unify them into the final short sentiment.
    """
    return "\n---\n".join(partial_results)

def get_partial_sentiment(text):
    """
    Runs chunk-based analysis for 'text', returning a big
    string of partial sentiment results.
    """
    return process_chunks(
        text,
        prompt_generator_fn=partial_sentiment_prompt,
        combine_fn=partial_sentiment_combine_fn,
        chunk_size=BASE_CHUNK_SIZE,
        parallel=True,       # parallel for speed
        max_workers=2,       # tweak as needed
        chunk_timeout=30     # shorter time
    )

###############################################################################
# 2) FINAL MERGE INTO A SHORT SENTIMENT
###############################################################################

def final_sentiment_prompt(partials_text):
    """
    We unify partial sentiment analyses into one short final result:
      1) Overall Hodlers chat group Sentiment: ...
      2) Sentiment Breakdown: ...
      3) One short concluding sentence
      (under 300 chars)
    """
    return (
        "We have multiple partial sentiment analyses:\n"
        f"{partials_text}\n\n"
        "Now produce a SINGLE, very short final sentiment result with the format:\n"
        "📊 Overall Hodlers chat group Sentiment: (Bullish 🚀, Bearish 🛑, or Neutral 🤔)\n"
        "🔍 Sentiment Breakdown: - Positive: X%, Neutral: Y%, Negative: Z%\n"
        "One short concluding sentence (max 80 characters).\n"
        "Keep the entire output under 300 characters total."
    )

def unify_into_short_sentiment(partials_text):
    """
    Calls the model once more to unify partial sentiments
    into a short final snippet. We do a local truncate if the model
    ignores instructions.
    """
    prompt = final_sentiment_prompt(partials_text)
    session = create_session_with_retry()
    final_text = call_openwebui(prompt, session=session, timeout=60)

    # Truncate if it disobeys
    if len(final_text) > 300:
        final_text = final_text[:290] + "..."
    return final_text

###############################################################################
# 3) Main Function Called by Handler
###############################################################################

def analyze_sentiment(messages):
    """
    1) Build text from messages.
    2) partial chunk-based sentiment
    3) unify partial results => short snippet
    """
    if not messages:
        logger.debug("No messages provided for sentiment analysis.")
        return "No messages found for sentiment analysis."

    text_to_analyze = "\n".join(f"@{msg['user']}: {msg['text']}" for msg in messages)

    partial_summaries = get_partial_sentiment(text_to_analyze)
    logger.debug("Finished partial sentiment. Now merging into short final...")

    final_result = unify_into_short_sentiment(partial_summaries)
    logger.debug(f"Final short sentiment length: {len(final_result)}")

    return final_result

