import logging
import os
from logging.handlers import RotatingFileHandler

def get_logger(job_id: str = "global", level: int = logging.INFO):
    logs_dir = os.path.join(os.getcwd(), "logs")
    os.makedirs(logs_dir, exist_ok=True)
    logger = logging.getLogger(f"aibuildx.{job_id}")
    if logger.handlers:
        return logger
    logger.setLevel(level)
    log_path = os.path.join(logs_dir, f"{job_id}.log")
    handler = RotatingFileHandler(log_path, maxBytes=5_000_000, backupCount=3)
    fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    handler.setFormatter(logging.Formatter(fmt))
    logger.addHandler(handler)
    # also print to console
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter(fmt))
    logger.addHandler(ch)
    return logger
