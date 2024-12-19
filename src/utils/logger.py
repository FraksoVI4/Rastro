import logging
import sys
from datetime import datetime
from pathlib import Path

class RastroLogger:
    def __init__(self):
        self.logger = logging.getLogger('rastro')
        self.logger.setLevel(logging.DEBUG)
        
        # Создаем директорию для логов если её нет
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # Создаем форматтер для логов
        self.formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%d.%m.%Y %H:%M:%S'
        )
        
        # Настраиваем хендлеры
        self.setup_handlers()

    def setup_handlers(self):
        """Настройка обработчиков логов"""
        # Файловый хендлер
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_handler = logging.FileHandler(
            self.log_dir / f'rastro_{timestamp}.log',
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(self.formatter)
        
        # Консольный хендлер
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(self.formatter)
        
        # Добавляем хендлеры
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def debug(self, message: str):
        self.logger.debug(message)

    def info(self, message: str):
        self.logger.info(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def error(self, message: str):
        self.logger.error(message)

    def critical(self, message: str):
        self.logger.critical(message)

# Создаем глобальный экземпляр логгера
rastro_logger = RastroLogger()

def setup_logger():
    """
    Функция для обратной совместимости.
    Настраивает и возвращает логгер в старом стиле.
    """
    return rastro_logger.logger

def get_logger():
    """
    Возвращает глобальный экземпляр логгера.
    """
    return rastro_logger