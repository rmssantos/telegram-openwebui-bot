# bot.py

from dotenv import load_dotenv
import time
import requests
import logging
from handlers import bot
from utils.logging_conf import setup_logging

load_dotenv()

if __name__ == "__main__":
    logger = setup_logging()
    logger.debug("Starting bot polling...")

    while True:
        try:
            bot.polling(timeout=65, long_polling_timeout=120)
        except requests.exceptions.ReadTimeout:
            logger.warning("Polling timed out. Retrying in 5 seconds...")
            time.sleep(5)
        except Exception as e:
            logger.error(f"Polling error: {e}. Retrying in 5 seconds...")
            time.sleep(5)

