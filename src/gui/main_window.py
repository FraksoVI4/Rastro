from PyQt6.QtWidgets import QMainWindow, QToolBar, QStatusBar, QSizePolicy, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from .canvas import Canvas
from tools.brush import BrushTool
from tools.eraser import EraserTool
import logging

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_tool = None
        self.initUI()
        self.setupShortcuts()
        
    def initUI(self):
        """Инициализация пользовательского интерфейса"""
        self.setWindowTitle('Rastro')
        self.setGeometry(100, 100, 800, 600)
        
        self.canvas = Canvas()
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, 
                                QSizePolicy.Policy.Expanding)
        self.setCentralWidget(self.canvas)
        
        self.createToolBar()
        
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        # Устанавливаем кисть по умолчанию
        self.select_tool("brush")
        
        logger.info("Главное окно инициализировано")

    def createToolBar(self):
        """Создание панели инструментов"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # Кнопка кисти
        brush_btn = QPushButton("Кисть")
        brush_btn.clicked.connect(lambda: self.select_tool("brush"))
        toolbar.addWidget(brush_btn)

        # Кнопка ластика
        eraser_btn = QPushButton("Ластик")
        eraser_btn.clicked.connect(lambda: self.select_tool("eraser"))
        toolbar.addWidget(eraser_btn)

        # Добавляем разделитель
        toolbar.addSeparator()

        # Кнопки отмены/повтора
        undo_btn = QPushButton("↶ Отменить")
        undo_btn.clicked.connect(self.canvas.undo)
        toolbar.addWidget(undo_btn)

        redo_btn = QPushButton("↷ Повторить")
        redo_btn.clicked.connect(self.canvas.redo)
        toolbar.addWidget(redo_btn)

    def setupShortcuts(self):
        """Настройка горячих клавиш"""
        # Быстрый выбор инструментов
        brush_action = QAction('Кисть', self)
        brush_action.setShortcut('B')
        brush_action.triggered.connect(lambda: self.select_tool("brush"))
        self.addAction(brush_action)

        eraser_action = QAction('Ластик', self)
        eraser_action.setShortcut('E')
        eraser_action.triggered.connect(lambda: self.select_tool("eraser"))
        self.addAction(eraser_action)

    def select_tool(self, tool_name):
        """Выбор инструмента"""
        if tool_name == "brush":
            self.current_tool = BrushTool()
            self.statusBar.showMessage("Выбран инструмент: Кисть")
            logger.info("Выбран инструмент: Кисть")
        elif tool_name == "eraser":
            self.current_tool = EraserTool()
            self.statusBar.showMessage("Выбран инструмент: Ластик")
            logger.info("Выбран инструмент: Ластик")