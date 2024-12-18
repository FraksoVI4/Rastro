from .base_tool import BaseTool
from PyQt6.QtGui import QPen
from PyQt6.QtCore import Qt

class BrushTool(BaseTool):
    def draw(self, canvas, pos, painter):
        painter.setPen(QPen(self.color, self.size, Qt.PenStyle.SolidLine))
        painter.drawLine(canvas.lastPoint, pos)