import logging
import os
import sys

class Logger:
    _instance = None

    @staticmethod
    def get_logger(name="QMBOS_Test", log_file=None):
        """
        Returns a configured logger instance.
        If log_file is provided, it adds a FileHandler.
        """
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        # Avoid adding duplicate handlers if get_logger is called multiple times
        if not logger.handlers:
            # 1. Console Handler (INFO and above) - Only add if not running under Pytest
            # Pytest handles console logging automatically via --log-cli-level=INFO
            if "pytest" not in sys.modules:
                console_handler = logging.StreamHandler(sys.stdout)
                console_handler.setLevel(logging.INFO)
                console_formatter = logging.Formatter(
                    '%(asctime)s [%(levelname)s] %(message)s',
                    datefmt='%H:%M:%S'
                )
                console_handler.setFormatter(console_formatter)
                logger.addHandler(console_handler)

            # 2. File Handler (DEBUG and above) - Only if log_file is provided
            if log_file:
                file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
                file_handler.setLevel(logging.DEBUG)
                file_formatter = logging.Formatter(
                    '%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
                file_handler.setFormatter(file_formatter)
                logger.addHandler(file_handler)

        return logger

# Global instance for easy import
log = Logger.get_logger()