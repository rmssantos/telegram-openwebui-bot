# services/bing_search_api.py
import os
import requests
import logging

logger = logging.getLogger(__name__)

BING_SEARCH_KEY = os.getenv("BING_SEARCH_KEY")  # e.g. 40154a43cfa349e...
BING_SEARCH_ENDPOINT = "https://api.bing.microsoft.com/v7.0/search"

def query_bing_api(query: str, count=3, market="en-US"):
    """
    Calls Bing Search REST API for the given query.
    Returns a list of dicts: [{"title": ..., "snippet": ..., "url": ...}, ...].
    """
    if not BING_SEARCH_KEY:
        logger.error("BING_SEARCH_KEY not set in .env!")
        return []

    headers = {"Ocp-Apim-Subscription-Key": BING_SEARCH_KEY}
    params = {
        "q": query,
        "count": count,
        "mkt": market,  # "en-US", "nl-NL", etc.
        "textDecorations": True,
        "textFormat": "HTML",
    }

    try:
        resp = requests.get(BING_SEARCH_ENDPOINT, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        logger.error(f"Bing Search error: {e}")
        return []

    # Extract results from data
    web_pages = data.get("webPages", {})
    values = web_pages.get("value", [])
    results = []
    for v in values:
        results.append({
            "title": v.get("name"),
            "snippet": v.get("snippet", ""),
            "url": v.get("url"),
        })
    return results

# Optional: Summarization step for final output
# e.g. chunk the combined text and pass to local model
def summarize_results(results):
    """
    Very naive example: 
    Combine snippet texts => feed to local/azure model => short summary.

    Replace with your real chunk-based approach from openwebui or azure openai.
    """
    if not results:
        return "No results from Bing."

    # Combine snippet texts
    combined_text = ""
    for i, r in enumerate(results, start=1):
        combined_text += f"Result {i}: {r['title']}\n{r['snippet']}\nURL: {r['url']}\n\n"

    # For illustration, just return the first 500 chars
    if len(combined_text) > 500:
        combined_text = combined_text[:500] + "... [truncated]"
    return combined_text

