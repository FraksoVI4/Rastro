from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPoint, QSize
from PyQt6.QtGui import QPainter, QImage, QPen, QColor
from utils.history_manager import HistoryManager
from tools.line import LineTool
import logging

logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)

class Canvas(QWidget):
    def __init__(self):
        super().__init__()
        self.color = QColor(Qt.GlobalColor.black)
        self.brush_size = 3
        self.history = HistoryManager()
        self.current_tool = None  # Добавляем инструмент прямо в Canvas
        self.initUI()
        
    def initUI(self):
        """Инициализация холста"""
        size = QSize(800, 600)  # Начальный размер холста
        self.image = QImage(size, QImage.Format.Format_RGB32)
        self.image.fill(Qt.GlobalColor.white)
        self.setFixedSize(size)
        self.drawing = False
        self.lastPoint = QPoint()
        self.history.push_state(self.image)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        logger.info(f"Холст инициализирован с размером {size}")

    def change_size(self, width, height):
        """
        Изменить размер холста
        """
        # Копируем текущую историю
        old_states = self.history.undo_stack.copy()
        
        # Создаем новые состояния с новым размером
        new_states = []
        for old_image in old_states:
            new_image = QImage(QSize(width, height), QImage.Format.Format_RGB32)
            new_image.fill(Qt.GlobalColor.white)
            painter = QPainter(new_image)
            painter.drawImage(0, 0, old_image)
            painter.end()
            new_states.append(new_image)
        
        # Обновляем размер текущего изображения
        new_image = QImage(QSize(width, height), QImage.Format.Format_RGB32)
        new_image.fill(Qt.GlobalColor.white)
        painter = QPainter(new_image)
        painter.drawImage(0, 0, self.image)
        painter.end()
        self.image = new_image
        
        # Обновляем виджет
        self.setFixedSize(width, height)
        
        # Обновляем историю с новыми размерами
        self.history.undo_stack = new_states
        self.history.redo_stack.clear()
        self.update()
        
        logger.debug(f"Изменен размер холста на {width}x{height}")

    def paintEvent(self, event):
        """Обработчик события перерисовки"""
        painter = QPainter(self)
        painter.drawImage(0, 0, self.image)
    
    def mousePressEvent(self, event):
        """Обработчик нажатия кнопки мыши"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            self.lastPoint = event.pos()
            if isinstance(self.current_tool, LineTool):
                self.temp_image = self.image.copy()  # Сохраняем копию для предпросмотра
            logger.debug(f"Нажатие мыши в позиции {event.pos()}")
    
    def mouseMoveEvent(self, event):
        """Обработчик движения мыши"""
        if event.buttons() & Qt.MouseButton.LeftButton and self.drawing:
            if isinstance(self.current_tool, LineTool):
                # Для линии - рисуем временное изображение
                self.image = self.temp_image.copy()
            
            painter = QPainter(self.image)
            if self.current_tool:
                self.current_tool.size = self.brush_size
                self.current_tool.color = self.color
                self.current_tool.draw(self, event.pos(), painter)
            painter.end()
            
            self.lastPoint = event.pos()
            self.update()
            logger.debug(f"Рисование до позиции {event.pos()}")
    
    def mouseReleaseEvent(self, event):
        """Обработчик отпускания кнопки мыши"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False
            
            if isinstance(self.current_tool, LineTool):
                self.current_tool.start_point = None  # Сбрасываем начальную точку
                
            self.history.push_state(self.image)
            logger.debug("Кнопка мыши отпущена")

    def undo(self):
        """Отмена последнего действия"""
        new_state = self.history.undo()
        if new_state:
            self.image = new_state
            self.update()
            logger.debug("Отмена действия применена")
    
    def redo(self):
        """Повтор отмененного действия"""
        new_state = self.history.redo()
        if new_state:
            self.image = new_state
            self.update()
            logger.debug("Повтор действия применен")

    def keyPressEvent(self, event):
        """Обработка нажатий клавиш"""
        if event.key() == Qt.Key.Key_Z and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.undo()
            event.accept()
            return
        elif event.key() == Qt.Key.Key_Z and event.modifiers() == (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier):
            self.redo()
            event.accept()
            return
        elif event.key() == Qt.Key.Key_Y and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.redo()
            event.accept()
            return
        super().keyPressEvent(event)