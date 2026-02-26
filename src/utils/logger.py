# src/utils/logger.py

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_FILE = "logs/pipeline.log"  # consolidated log
MAX_BYTES = 5 * 1024 * 1024     # 5 MB
BACKUP_COUNT = 3                # keep last 3 log files

def get_logger(name: str, level=logging.INFO):
    """
    Returns a logger that logs to console and a single consolidated file with rollover.
    Log format: YYYY-MM-DD HH:MM:SS | LEVEL | filename::function | message
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        # Formatter including file name and function
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(filename)s::%(funcName)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        # Rotating file handler
        Path("logs").mkdir(parents=True, exist_ok=True)
        fh = RotatingFileHandler(LOG_FILE, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT)
        fh.setLevel(level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger