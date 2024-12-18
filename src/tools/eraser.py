from .base_tool import BaseTool
from PyQt6.QtGui import QPen
from PyQt6.QtCore import Qt

class EraserTool(BaseTool):
    def draw(self, canvas, pos, painter):
        self.color = Qt.GlobalColor.white  # Всегда белый цвет для ластика
        painter.setPen(QPen(self.color, self.size, Qt.PenStyle.SolidLine))
        painter.drawLine(canvas.lastPoint, pos)