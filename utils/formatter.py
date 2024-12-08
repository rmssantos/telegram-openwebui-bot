# utils/formatter.py

import re

def sanitize_html(summary):
    """
    Removes unsupported HTML tags and ensures only allowed tags are present.
    Allowed tags: <b>, <strong>, <i>, <em>, <a href="...">
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
    Replaces Markdown bold syntax **text** with HTML <b>text</b>
    Also ensures that usernames within bold tags are prefixed with '@'
    """
    # Replace Markdown bold with HTML bold
    sanitized_summary = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', summary)

    # Ensure usernames are prefixed with '@' within bold tags
    # This regex finds <b>Username:</b> and replaces it with <b>@Username:</b>
    sanitized_summary = re.sub(r'<b>([^@][^:]+):</b>', r'<b>@\1:</b>', sanitized_summary)

    return sanitized_summary

