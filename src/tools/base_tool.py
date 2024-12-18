from abc import ABC, abstractmethod
from PyQt6.QtCore import QPoint
from PyQt6.QtGui import QPainter

class BaseTool(ABC):
    def __init__(self):
        self.color = None
        self.size = 1

    @abstractmethod
    def draw(self, canvas, pos: QPoint, painter: QPainter):
        """
        Абстрактный метод для рисования
        :param canvas: Холст для рисования
        :param pos: Позиция курсора
        :param painter: Объект QPainter
        """
        pass