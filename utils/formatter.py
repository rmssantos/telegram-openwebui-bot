# utils/formatter.py

import re

def sanitize_html(summary):
    """
    Removes unsupported HTML tags and ensures only allowed tags are present.
    Allowed tags: <b>, <strong>, <i>, <em>, <a href="...">.
    """
    # Define allowed tags
    allowed_tags = ['b', 'strong', 'i', 'em', 'a']

    # Regex pattern to match all HTML tags not in the allowed list
    pattern = r'</?(?!(' + '|'.join(allowed_tags) + r'))\w+[^>]*>'

    # Remove all tags not in the allowed list
    sanitized_summary = re.sub(pattern, '', summary, flags=re.IGNORECASE)

    return sanitized_summary


def replace_markdown_bold(summary):
    """
    Replaces Markdown bold syntax **text** with HTML <b>text</b>.
    """
    return re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', summary)


def add_emoticons_to_summary(summary):
    """
    Enhances a plain text summary by adding category-specific emoticons.
    """
    topic_emojis = {
        "growth": "🚀",
        "trending": "🔥",
        "progress": "🌱",
        "debate": "🤔",
        "warning": "⚠️",
        "positive": "📈",
    }

    enhanced_summary = ""
    for line in summary.split("\n"):
        if any(keyword in line.lower() for keyword in ["growth", "launch", "new feature"]):
            line = f"{topic_emojis['growth']} {line}"
        elif any(keyword in line.lower() for keyword in ["trend", "buzz", "hot topic"]):
            line = f"{topic_emojis['trending']} {line}"
        elif any(keyword in line.lower() for keyword in ["progress", "develop", "update"]):
            line = f"{topic_emojis['progress']} {line}"
        elif any(keyword in line.lower() for keyword in ["discuss", "question", "debate"]):
            line = f"{topic_emojis['debate']} {line}"
        elif any(keyword in line.lower() for keyword in ["warn", "critical", "issue"]):
            line = f"{topic_emojis['warning']} {line}"
        elif any(keyword in line.lower() for keyword in ["success", "positive", "gain"]):
            line = f"{topic_emojis['positive']} {line}"
        enhanced_summary += line + "\n"

    return enhanced_summary.strip()


def markdown_to_telegram_html(text: str) -> str:
    """
    Converts a subset of Markdown-like syntax to Telegram-compatible HTML:
      - ### or any heading => <b>heading text</b>
      - **bold** => <b>bold</b>
      - [text](url) => <a href="url">text</a>
    Then sanitizes to remove any unsupported HTML.
    """

    # Headings (e.g. ### Step 1:) => <b>Step 1:</b>
    text = re.sub(r'^(#{1,6})\s*(.*)', r'<b>\2</b>', text, flags=re.MULTILINE)

    # Bold: **text** => <b>text</b>
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)

    # Links: [text](url) => <a href="url">text</a>
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', text)

    # Finally, sanitize
    text = sanitize_html(text)

    return text

