import logging
import sys
from datetime import datetime

def setup_logger():
    """Настройка системы логирования"""
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # Создаем форматтер для логов с русской локализацией
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%d.%m.%Y %H:%M:%S'
    )
    
    # Хендлер для записи в файл
    file_handler = logging.FileHandler(
        f'log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Хендлер для вывода в консоль
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)