from .base_tool import BaseTool
from PyQt6.QtGui import QPen, QBrush
from PyQt6.QtCore import Qt

class FillTool(BaseTool):
    def draw(self, canvas, pos, painter):
        # Получаем текущий цвет
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(self.color, 1, Qt.PenStyle.NoPen))
        painter.drawRect(0, 0, canvas.width(), canvas.height())