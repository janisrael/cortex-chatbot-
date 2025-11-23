# logging_config.py
import logging
from logging.handlers import RotatingFileHandler

def configure_logging():
    log_file = 'app.log'
    max_log_size = 20 * 1024 * 1024  # 20 MB
    backup_count = 3

    handler = RotatingFileHandler(log_file, mode='a', maxBytes=max_log_size, backupCount=backup_count)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)
