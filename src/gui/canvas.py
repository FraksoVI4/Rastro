from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPainter, QImage, QPen, QColor  # Добавляем QColor
import logging

logger = logging.getLogger(__name__)

class Canvas(QWidget):
    def __init__(self):
        super().__init__()
        # Добавляем начальные значения
        self.color = QColor(Qt.GlobalColor.black)  # Черный цвет по умолчанию
        self.brush_size = 3  # Размер кисти по умолчанию
        self.initUI()
        
    def initUI(self):
        """Инициализация холста"""
        size = self.size()
        self.image = QImage(size, QImage.Format.Format_RGB32)
        self.image.fill(Qt.GlobalColor.white)
        self.drawing = False
        self.lastPoint = QPoint()
        
        logger.info("Холст инициализирован")
    def resizeEvent(self, event):
        """Обработчик изменения размера окна"""
        # Создаем новое изображение нового размера
        newImage = QImage(event.size(), QImage.Format.Format_RGB32)
        newImage.fill(Qt.GlobalColor.white)
        
        # Отрисовываем старое изображение на новом
        painter = QPainter(newImage)
        painter.drawImage(QPoint(0, 0), self.image)
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
            painter.setPen(QPen(self.color, self.brush_size, Qt.PenStyle.SolidLine))
            painter.drawLine(self.lastPoint, event.pos())
            self.lastPoint = event.pos()
            self.update()
            logger.debug(f"Рисование линии до позиции {event.pos()}")

    def mouseReleaseEvent(self, event):
        """Обработчик отпускания кнопки мыши"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False
            logger.debug("Кнопка мыши отпущена")
            