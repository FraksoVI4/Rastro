from PyQt6.QtGui import QImage, QPainter
from PyQt6.QtCore import Qt, QPoint
import logging

logger = logging.getLogger(__name__)

class HistoryManager:
    def __init__(self, max_steps=30):
        self.undo_stack = []
        self.redo_stack = []
        self.max_steps = max_steps
        logger.info(f"Инициализирован менеджер истории (макс. шагов: {max_steps})")
    
    def push_state(self, image: QImage):
        """Сохранить новое состояние"""
        # Создаем полную копию изображения с сохранением размера
        state = QImage(image.size(), image.format())
        state.fill(Qt.GlobalColor.white)
        
        painter = QPainter(state)
        painter.drawImage(QPoint(0, 0), image)
        painter.end()
        
        self.undo_stack.append(state)
        self.redo_stack.clear()
        
        if len(self.undo_stack) > self.max_steps:
            self.undo_stack.pop(0)
        
        logger.debug(f"Сохранено новое состояние (всего: {len(self.undo_stack)}, размер: {state.size()})")
    
    def undo(self) -> QImage:
        """Отменить последнее действие"""
        if len(self.undo_stack) > 1:
            current_state = self.undo_stack.pop()
            self.redo_stack.append(current_state)
            previous_state = self.undo_stack[-1]
            
            # Создаем копию предыдущего состояния
            restored_state = QImage(previous_state.size(), previous_state.format())
            restored_state.fill(Qt.GlobalColor.white)
            
            painter = QPainter(restored_state)
            painter.drawImage(QPoint(0, 0), previous_state)
            painter.end()
            
            logger.info(f"Отмена действия (размер: {restored_state.size()})")
            return restored_state
        return None
    
    def redo(self) -> QImage:
        """Повторить отмененное действие"""
        if self.redo_stack:
            state = self.redo_stack.pop()
            
            # Создаем копию состояния
            restored_state = QImage(state.size(), state.format())
            restored_state.fill(Qt.GlobalColor.white)
            
            painter = QPainter(restored_state)
            painter.drawImage(QPoint(0, 0), state)
            painter.end()
            
            self.undo_stack.append(restored_state)
            logger.info(f"Повтор действия (размер: {restored_state.size()})")
            return restored_state
        return None
    
    def can_undo(self) -> bool:
        """Проверка возможности отмены"""
        return len(self.undo_stack) > 1
    
    def can_redo(self) -> bool:
        """Проверка возможности повтора"""
        return len(self.redo_stack) > 0