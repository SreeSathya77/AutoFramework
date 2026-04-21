import logging
import os
import sys
from datetime import datetime

class Logger:
    @staticmethod
    def get_logger():
        logger = logging.getLogger("QA_QM_BOS_REG")
        if not logger.handlers:
            logger.setLevel(logging.INFO)
            
            # Create logs directory if not exists
            if not os.path.exists("logs"):
                os.makedirs("logs")
                
            timestamp = datetime.now().strftime("%Y%m%d")

            # File handler - UTF-8 encoding for full Unicode support
            file_handler = logging.FileHandler(
                f"logs/execution_{timestamp}.log",
                encoding='utf-8'
            )
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            
            # Console handler with Unicode handling
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            
            # Add error handler for Unicode encoding issues on Windows
            # This replaces unencodable characters instead of raising errors
            console_handler.setLevel(logging.DEBUG)

            # Set encoding to UTF-8 if possible, with 'replace' error handler
            if hasattr(console_handler, 'stream') and hasattr(console_handler.stream, 'reconfigure'):
                try:
                    console_handler.stream.reconfigure(encoding='utf-8', errors='replace')
                except AttributeError:
                    pass

            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        return logger
