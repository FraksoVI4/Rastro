import sys
import os
from pathlib import Path

# Добавляем текущую директорию в путь для импортов
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow
from utils.logger import setup_logger

def main():
    # Настраиваем логирование
    setup_logger()
    
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Ошибка: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()