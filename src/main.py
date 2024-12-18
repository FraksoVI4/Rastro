import sys
import logging
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow
from utils.logger import setup_logger

def main():
    # Настраиваем логирование
    setup_logger()
    logger = logging.getLogger(__name__)
    
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        logger.error(f"Приложение вылетело: {str(e)}")
        raise

if __name__ == "__main__":
    main()