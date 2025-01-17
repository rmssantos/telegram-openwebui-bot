# utils/logging_conf.py

import logging
from logging.handlers import RotatingFileHandler
from config import LOG_LEVEL

def setup_logging():
    logger = logging.getLogger()
    
    # Prevent adding multiple handlers if setup_logging is called multiple times
    if not logger.handlers:
        # Create a rotating file handler that rotates at 5 MB and keeps 5 backups.
        rotating_handler = RotatingFileHandler(
            "bot.log",
            maxBytes=5 * 1024 * 1024,
            backupCount=5,
            encoding='utf-8'
        )
    
        # Set the level of the rotating handler
        rotating_handler.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
    
        # Create a formatter and set it for the handler
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        rotating_handler.setFormatter(formatter)
    
        # Add handlers to the logger
        logger.addHandler(rotating_handler)
    
    return logger

