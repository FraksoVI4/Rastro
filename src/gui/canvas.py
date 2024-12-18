from PyQt6.QtWidgets import QWidget, QMainWindow
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPainter, QImage, QPen, QColor
from utils.history_manager import HistoryManager
import logging

logger = logging.getLogger(__name__)

class Canvas(QWidget):
    def __init__(self):
        super().__init__()
        self.color = QColor(Qt.GlobalColor.black)
        self.brush_size = 3
        self.history = HistoryManager()
        self.initUI()
        
    def initUI(self):
        """Инициализация холста"""
        size = self.size()
        self.image = QImage(size, QImage.Format.Format_RGB32)
        self.image.fill(Qt.GlobalColor.white)
        self.drawing = False
        self.lastPoint = QPoint()
        self.history.push_state(self.image)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        logger.info("Холст инициализирован")

    def resizeEvent(self, event):
        """Обработчик изменения размера окна"""
        newImage = QImage(event.size(), QImage.Format.Format_RGB32)
        newImage.fill(Qt.GlobalColor.white)
        
        painter = QPainter(newImage)
        painter.drawImage(QPoint(0, 0), self.image)
        painter.end()
        
        self.image = newImage
        super().resizeEvent(event)
    
    def paintEvent(self, event):
        """Обработчик события перерисовки"""
        painter = QPainter(self)
        painter.drawImage(0, 0, self.image)
    
    def mousePressEvent(self, event):
        """Обработчик нажатия кнопки мыши"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            self.lastPoint = event.pos()
            logger.debug(f"Нажатие мыши в позиции {event.pos()}")
    
    def mouseMoveEvent(self, event):
        """Обработчик движения мыши"""
        if event.buttons() & Qt.MouseButton.LeftButton and self.drawing:
            painter = QPainter(self.image)
            if isinstance(self.parent(), QMainWindow):
                tool = self.parent().current_tool
                if tool:
                    tool.size = self.brush_size
                    tool.color = self.color
                    tool.draw(self, event.pos(), painter)
            self.lastPoint = event.pos()
            self.update()
            logger.debug(f"Рисование линии до позиции {event.pos()}")
    
    def mouseReleaseEvent(self, event):
        """Обработчик отпускания кнопки мыши"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False
            self.history.push_state(self.image)
            logger.debug("Кнопка мыши отпущена")

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