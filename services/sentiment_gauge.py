# services/sentiment_gauge.py
import requests
import io
from PIL import Image

def get_fear_greed_value():
    """
    Fetches the current Fear & Greed Index from alternative.me.
    Returns (value, classification) e.g. (74, "Greed").
    """
    url = "https://api.alternative.me/fng/"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    item = data["data"][0]
    value = int(item["value"])
    classification = item["value_classification"]
    return value, classification

def send_resized_fear_greed_image(bot, chat_id, value, classification, width=250):
    """
    Downloads the official chart from alternative.me, resizes it,
    and sends it to Telegram with the given (value, classification).
    """
    chart_url = "https://alternative.me/crypto/fear-and-greed-index.png"
    try:
        resp = requests.get(chart_url, timeout=10)
        resp.raise_for_status()

        img_original = Image.open(io.BytesIO(resp.content))
        orig_w, orig_h = img_original.size
        ratio = orig_h / float(orig_w)
        new_w = width
        new_h = int(ratio * new_w)

        img_resized = img_original.resize((new_w, new_h), Image.LANCZOS)

        img_bytes = io.BytesIO()
        img_resized.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        caption_txt = f"Global Crypto Market Fear & Greed Index: {value} ({classification})"
        bot.send_photo(chat_id, photo=img_bytes, caption=caption_txt)

    except Exception as e:
        bot.send_message(chat_id, f"Unable to fetch Fear & Greed chart: {e}")

