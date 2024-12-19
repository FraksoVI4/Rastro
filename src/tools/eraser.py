# tools/eraser.py

from .base_tool import BaseTool
from PyQt6.QtGui import QPen, QColor
from PyQt6.QtCore import Qt

class EraserTool(BaseTool):
    def __init__(self):
        super().__init__()
        # Явно инициализируем белый цвет
        self._color = QColor(Qt.GlobalColor.white)

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        # Всегда устанавливаем белый, игнорируя входящий цвет
        self._color = QColor(Qt.GlobalColor.white)

    def draw(self, canvas, pos, painter):
        painter.setPen(QPen(self.color, self.size, Qt.PenStyle.SolidLine))
        painter.drawLine(canvas.lastPoint, pos)