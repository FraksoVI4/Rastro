from PyQt6.QtGui import QImage
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
        # Создаем полную копию изображения
        state = QImage(image)
        
        self.undo_stack.append(state)
        self.redo_stack.clear()
        
        if len(self.undo_stack) > self.max_steps:
            self.undo_stack.pop(0)
        
        logger.debug(f"Сохранено новое состояние (всего: {len(self.undo_stack)})")
    
    def undo(self) -> QImage:
        """Отменить последнее действие"""
        if len(self.undo_stack) > 1:
            current_state = self.undo_stack.pop()
            self.redo_stack.append(current_state)
            previous_state = self.undo_stack[-1]
            logger.info("Отмена действия")
            return QImage(previous_state)
        return None
    
    def redo(self) -> QImage:
        """Повторить отмененное действие"""
        if self.redo_stack:
            state = self.redo_stack.pop()
            self.undo_stack.append(state)
            logger.info("Повтор действия")
            return QImage(state)
        return None
    
    def can_undo(self) -> bool:
        """Проверка возможности отмены"""
        return len(self.undo_stack) > 1
    
    def can_redo(self) -> bool:
        """Проверка возможности повтора"""
        return len(self.redo_stack) > 0