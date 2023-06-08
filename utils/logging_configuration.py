import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from logging import Logger
from typing import Dict, Union


class LoggingConfigurator:

    @staticmethod
    def get_logger(config: Dict[str, Union[str, int]], log_file_name: str) -> Logger:
        logger = logging.getLogger()
        if logger.hasHandlers():
            logger.handlers.clear()

        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', '%m-%d-%Y %H:%M:%S')
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(logging.INFO)
        stdout_handler.setFormatter(formatter)

        log_folder_path = Path(config['LOG_PATH'])
        log_folder_path.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(filename=log_folder_path.joinpath(log_file_name), mode='a',
                                           maxBytes=50*1024*1024, backupCount=10)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(stdout_handler)

        return logger
