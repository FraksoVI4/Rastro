from .base_tool import BaseTool
from PyQt6.QtGui import QPen, QPainter
from PyQt6.QtCore import Qt, QPoint

class LineTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.start_point = None

    def draw(self, canvas, pos, painter):
        """
        Рисование линии от начальной точки до текущей позиции
        """
        if not self.start_point:
            self.start_point = pos
            return
            
        pen = QPen(self.color, self.size, Qt.PenStyle.SolidLine)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawLine(self.start_point, pos)