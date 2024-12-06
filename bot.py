from dotenv import load_dotenv
load_dotenv()

from handlers import bot
from utils.logging_conf import setup_logging

if __name__ == "__main__":
    logger = setup_logging()
    logger.debug("Starting bot polling...")
    bot.polling(timeout=60, long_polling_timeout=60)

