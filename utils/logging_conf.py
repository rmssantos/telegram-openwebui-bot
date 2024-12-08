import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    # Configure a rotating file handler that rotates at 5 MB and keeps 5 backups.
    rotating_handler = RotatingFileHandler(
        "bot.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding='utf-8'
    )

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(),
            rotating_handler
        ]
    )
    logger = logging.getLogger(__name__)
    return logger

