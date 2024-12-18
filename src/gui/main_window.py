from PyQt6.QtWidgets import (QMainWindow, QToolBar, QStatusBar, 
                           QSizePolicy)  # Добавляем QSizePolicy
from PyQt6.QtCore import Qt
from .canvas import Canvas
import logging

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        """Инициализация пользовательского интерфейса"""
        self.setWindowTitle('Простой растровый редактор')
        self.setGeometry(100, 100, 800, 600)
        
        self.canvas = Canvas()
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, 
                                QSizePolicy.Policy.Expanding)
        self.setCentralWidget(self.canvas)
        
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        logger.info("Главное окно инициализировано")
    
    def createToolBar(self):
        """Создание панели инструментов"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        # Здесь будем добавлять инструменты