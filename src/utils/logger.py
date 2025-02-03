import os
import logging
from logging.handlers import RotatingFileHandler


def get_logger(name: str, error_log_file: str = "logs/app_error.log", info_log_file: str = "logs/app_info.log"):
    os.makedirs(os.path.dirname(error_log_file), exist_ok=True)

    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers
    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    error_handler = RotatingFileHandler(error_log_file, maxBytes=10*1024*1024, backupCount=5)
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)

    info_handler = RotatingFileHandler(info_log_file, maxBytes=10*1024*1024, backupCount=5)
    info_handler.setFormatter(formatter)
    info_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    logger.addHandler(error_handler)
    logger.addHandler(info_handler)
    logger.addHandler(console_handler)

    return logger