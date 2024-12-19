import sys
from pathlib import Path

# Добавляем корневую директорию проекта в PYTHONPATH
current_dir = Path(__file__).parent  # utils/
project_root = current_dir.parent    # src/
sys.path.insert(0, str(project_root))

import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QImage, QColor, QPainter, QMouseEvent
from PyQt6.QtCore import Qt, QPoint, QEvent, QPointF
from gui.main_window import MainWindow
from gui.canvas import Canvas
from tools.brush import BrushTool
from tools.eraser import EraserTool
from tools.line import LineTool
from tools.fill import FillTool
from utils.history_manager import HistoryManager
import logging
from utils.logger import rastro_logger as logger

# Получаем Qt приложение из test_runner
from test_runner import get_qt_app

@pytest.fixture(scope="session")
def app():
    """Фикстура для Qt приложения"""
    return get_qt_app()

@pytest.fixture
def window(app):
    """Фикстура для главного окна"""
    window = MainWindow()
    yield window
    window.close()

@pytest.fixture
def canvas(app):
    """Фикстура для холста"""
    canvas = Canvas()
    canvas.resize(400, 300)  
    canvas.image.fill(Qt.GlobalColor.white)  # Явно заполняем белым
    canvas.current_tool = BrushTool()  # Устанавливаем инструмент
    canvas.current_tool.size = 5  # Устанавливаем размер
    canvas.current_tool.color = QColor(Qt.GlobalColor.black)  # Устанавливаем цвет
    return canvas

def create_mouse_event(pos: QPoint, button=Qt.MouseButton.LeftButton, type=QEvent.Type.MouseButtonPress) -> QMouseEvent:
    """Создание события мыши"""
    return QMouseEvent(
        type,
        QPointF(pos),
        QPointF(pos),
        button,
        button,
        Qt.KeyboardModifier.NoModifier
    )

class TestBlackBox:
    """Тестирование методом черного ящика"""
    
    def test_window_creation(self, window):
        """Создание главного окна"""
        assert window.windowTitle() == 'Rastro'
        assert window.size().width() >= 800
        assert window.size().height() >= 600
        
    def test_tools_availability(self, window):
        """Проверка наличия всех инструментов"""
        tools_map = {
            "brush": "Кисть",
            "line": "Линия",
            "eraser": "Ластик",
            "fill": "Заливка"
        }
        
        for tool_name, expected_text in tools_map.items():
            window.select_tool(tool_name)
            assert expected_text in window.tool_label.text()
            
    def test_drawing_operations(self, canvas):
        """Проверка операций рисования"""
        # Убеждаемся что холст белый
        assert canvas.image.pixelColor(0, 0).rgb() == QColor(Qt.GlobalColor.white).rgb()
        
        # Устанавливаем инструмент для рисования
        canvas.current_tool = BrushTool()
        canvas.current_tool.color = QColor(Qt.GlobalColor.black)
        canvas.current_tool.size = 5

        # Рисуем линию
        start = QPoint(50, 50)
        end = QPoint(100, 100)
        canvas.lastPoint = start  # Важно установить lastPoint
        
        # Симулируем рисование
        canvas.mousePressEvent(create_mouse_event(start))
        canvas.mouseMoveEvent(create_mouse_event(end, type=QEvent.Type.MouseMove))
        canvas.mouseReleaseEvent(create_mouse_event(end, type=QEvent.Type.MouseButtonRelease))
        
        # Проверяем что точка стала черной
        middle_point = QPoint(75, 75)  # Точка на пути линии
        color = canvas.image.pixelColor(middle_point)
        assert color.rgb() == QColor(Qt.GlobalColor.black).rgb()
        
    def test_undo_redo(self, canvas):
        """Проверка отмены/повтора действий"""
        # Запоминаем начальное состояние (белый холст)
        canvas.history.push_state(canvas.image)

        # Рисуем черную линию
        start = QPoint(50, 50)
        end = QPoint(100, 100)
        canvas.lastPoint = start
        canvas.current_tool.color = QColor(Qt.GlobalColor.black)
        
        canvas.mousePressEvent(create_mouse_event(start))
        canvas.mouseMoveEvent(create_mouse_event(end, type=QEvent.Type.MouseMove))
        canvas.mouseReleaseEvent(create_mouse_event(end, type=QEvent.Type.MouseButtonRelease))

        # Проверяем что линия нарисовалась
        middle_point = QPoint(75, 75)
        assert canvas.image.pixelColor(middle_point).rgb() == QColor(Qt.GlobalColor.black).rgb()
        
        # Отменяем действие
        canvas.undo()
        assert canvas.image.pixelColor(middle_point).rgb() == QColor(Qt.GlobalColor.white).rgb()
        
        # Повторяем действие
        canvas.redo()
        assert canvas.image.pixelColor(middle_point).rgb() == QColor(Qt.GlobalColor.black).rgb()
        
    def test_color_selection(self, canvas):
        """Проверка выбора цвета"""
        initial_color = canvas.current_tool.color
        new_color = QColor(255, 0, 0)  # Красный
        
        canvas.current_tool.color = new_color
        assert canvas.current_tool.color.rgb() == new_color.rgb()
        assert canvas.current_tool.color.rgb() != initial_color.rgb()

class TestWhiteBox:
    """Тестирование методом белого ящика"""
    
    def test_history_manager_internals(self):
        """Проверка внутренней работы менеджера истории"""
        history = HistoryManager(max_steps=3)
        
        test_image = QImage(100, 100, QImage.Format.Format_RGB32)
        colors = [Qt.GlobalColor.red, Qt.GlobalColor.green, Qt.GlobalColor.blue, Qt.GlobalColor.black]
        
        for color in colors:
            test_image.fill(color)
            history.push_state(test_image)
            
        assert len(history.undo_stack) == 3
        oldest_color = history.undo_stack[0].pixelColor(0, 0)
        assert oldest_color.rgb() == QColor(Qt.GlobalColor.green).rgb()
    
    def test_tool_inheritance(self):
        """Проверка правильности наследования инструментов"""
        tools = [BrushTool(), LineTool(), EraserTool(), FillTool()]
        
        for tool in tools:
            assert hasattr(tool, 'draw')
            assert hasattr(tool, 'color')
            assert hasattr(tool, 'size')
            
    def test_eraser_implementation(self):
        """Проверка реализации ластика"""
        eraser = EraserTool()
        
        # После создания цвет должен быть белым
        assert eraser.color is not None
        assert isinstance(eraser.color, QColor)
        assert eraser.color == QColor(Qt.GlobalColor.white)
        
        # Пытаемся установить другой цвет
        test_color = QColor(Qt.GlobalColor.black)
        eraser.color = test_color
        
        # Цвет должен остаться белым
        assert eraser.color == QColor(Qt.GlobalColor.white)
        
        # Дополнительная проверка компонентов цвета
        assert eraser.color.red() == 255
        assert eraser.color.green() == 255
        assert eraser.color.blue() == 255
    def test_line_tool_state(self):
        """Проверка состояния инструмента линии"""
        line_tool = LineTool()
        assert line_tool.start_point is None
        
        canvas_mock = type('Canvas', (), {'lastPoint': QPoint(10, 10)})
        painter = QPainter()
        
        line_tool.draw(canvas_mock, QPoint(10, 10), painter)
        assert line_tool.start_point == QPoint(10, 10)

def test_error_handling(caplog):
    """Проверка обработки ошибок"""
    caplog.set_level(logging.ERROR)
    
    # Логируем тестовую ошибку
    logger.error("тестовая ошибка работы с файлом")
    
    # Проверяем лог
    assert len(caplog.records) > 0
    assert any("тестовая ошибка" in record.message.lower() for record in caplog.records)

def test_canvas_resize(canvas):
    """Проверка изменения размера холста"""
    initial_width = canvas.width()
    initial_height = canvas.height()
    
    new_width = initial_width * 2
    new_height = initial_height * 2
    
    canvas.change_size(new_width, new_height)
    assert canvas.width() == new_width
    assert canvas.height() == new_height

if __name__ == '__main__':
    pytest.main([__file__, '-v'])