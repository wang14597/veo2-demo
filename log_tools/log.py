import logging
import os
from logging.handlers import RotatingFileHandler


def get_logger(name, to_file=False):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    if to_file:
        log_dir = os.path.join("logs", name)
        os.makedirs(log_dir, exist_ok=True)

        file_handler = RotatingFileHandler(
            filename=os.path.join(log_dir, f"{name}.log"),
            maxBytes=1024 * 1024 * 2,
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger.addHandler(console_handler)

    return logger


logger = get_logger("veo2-demo", to_file=False)
