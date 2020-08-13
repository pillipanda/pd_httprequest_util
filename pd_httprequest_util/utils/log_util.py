import os
from typing import Optional
from loguru import logger


class LoggerUtil(object):
    def __init__(self,
                 logger_name: str,
                 base_path='/tmp',
                 clear_day: Optional[int] = None):
        logger.add(
            os.path.join(base_path, f'{logger_name}.log'),
            level="INFO",
            rotation="00:00",
            compression="zip",
            retention=f"{clear_day} day" if isinstance(clear_day, int) else None,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
        )
        self._instance = logger

    def getLogger(self):
        return self._instance
