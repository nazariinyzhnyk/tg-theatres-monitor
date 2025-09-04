import logging
import os.path
import sys
from functools import lru_cache
from logging import Logger


@lru_cache(maxsize=1)
def get_logger(name: str = "monitor", file_path: str | None = None) -> Logger:
    logger = Logger(name)
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)

    file_handler = logging.FileHandler(
        file_path if file_path else os.path.join(os.path.dirname(__file__), "app.log"), mode="a", encoding="utf-8"
    )
    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(fmt="%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    file_handler.setFormatter(formatter)
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.addHandler(file_handler)

    return logger


logger = get_logger()
