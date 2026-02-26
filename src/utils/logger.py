"""
Logger Utility
Author: Deanesh Takkallapati
Purpose: Centralized logging for ETL, transformation, and ML modules
"""

import logging
import os

def get_logger(name: str, log_file: str = "etl_pipeline.log") -> logging.Logger:
    """
    Returns a configured logger instance.
    Logs to both console and file.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        # Ensure log directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # File handler
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.INFO)
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        logger.addHandler(fh)
        logger.addHandler(ch)

    return logger