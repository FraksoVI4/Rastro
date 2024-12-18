from PyQt6.QtWidgets import (QMainWindow, QToolBar, QStatusBar, QSizePolicy, 
                             QPushButton, QMenu, QDialog, QVBoxLayout, QHBoxLayout,
                             QLabel, QSpinBox, QScrollArea, QWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from .canvas import Canvas
from tools.brush import BrushTool
from tools.eraser import EraserTool
from tools.line import LineTool
import logging

logger = logging.getLogger(__name__)


class ResizeDialog(QDialog):
    def __init__(self, current_width, current_height, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Размер холста")
        
        layout = QVBoxLayout()
        
        # Поля для ввода размеров
        size_layout = QHBoxLayout()
        
        # Ширина
        width_layout = QVBoxLayout()
        width_layout.addWidget(QLabel("Ширина:"))
        self.width_spin = QSpinBox()
        self.width_spin.setRange(100, 3000)
        self.width_spin.setValue(current_width)
        width_layout.addWidget(self.width_spin)
        
        # Высота
        height_layout = QVBoxLayout()
        height_layout.addWidget(QLabel("Высота:"))
        self.height_spin = QSpinBox()
        self.height_spin.setRange(100, 3000)
        self.height_spin.setValue(current_height)
        height_layout.addWidget(self.height_spin)
        
        size_layout.addLayout(width_layout)
        size_layout.addLayout(height_layout)
        layout.addLayout(size_layout)
        
        # Кнопки
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def get_size(self):
        return self.width_spin.value(), self.height_spin.value()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setupShortcuts()
        
    def initUI(self):
        """Инициализация пользовательского интерфейса"""
        self.setWindowTitle('Rastro')
        self.setGeometry(100, 100, 800, 600)
        
        # Создаём холст
        self.canvas = Canvas()
        
        # Создаём область прокрутки
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.canvas)
        scroll_area.setWidgetResizable(False)  # Важно установить False, чтобы размер холста не менялся
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.setCentralWidget(scroll_area)
        
        # Создаём меню
        menubar = self.menuBar()
        
        # Меню изображения
        image_menu = menubar.addMenu('Изображение')
        resize_action = QAction('Размер холста...', self)
        resize_action.setShortcut('Ctrl+R')
        resize_action.triggered.connect(self.show_resize_dialog)
        image_menu.addAction(resize_action)
        
        self.createToolBar()
        
        # Создаем статусбар с постоянными элементами
        self.statusBar = QStatusBar()
        self.tool_label = QLabel("Инструмент: Кисть")
        self.size_label = QLabel(f"Размер холста: {self.canvas.width()}x{self.canvas.height()}")
        self.statusBar.addPermanentWidget(self.tool_label)
        self.statusBar.addPermanentWidget(self.size_label)
        self.setStatusBar(self.statusBar)
        
        self.select_tool("brush")
        logger.info("Главное окно инициализировано")

    def show_resize_dialog(self):
        """Показать диалог изменения размера"""
        dialog = ResizeDialog(self.canvas.width(), self.canvas.height(), self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            width, height = dialog.get_size()
            self.canvas.change_size(width, height)
            self.size_label.setText(f"Размер холста: {width}x{height}")
            logger.info(f"Изменен размер холста на {width}x{height}")

    def createToolBar(self):
        """Создание панели инструментов"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # Кнопка кисти
        brush_btn = QPushButton("Кисть")
        brush_btn.clicked.connect(lambda: self.select_tool("brush"))
        toolbar.addWidget(brush_btn)

        # Кнопка линии
        line_btn = QPushButton("Линия")
        line_btn.clicked.connect(lambda: self.select_tool("line"))
        toolbar.addWidget(line_btn)

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

        line_action = QAction('Линия', self)
        line_action.setShortcut('L')
        line_action.triggered.connect(lambda: self.select_tool("line"))
        self.addAction(line_action)

        eraser_action = QAction('Ластик', self)
        eraser_action.setShortcut('E')
        eraser_action.triggered.connect(lambda: self.select_tool("eraser"))
        self.addAction(eraser_action)

    def select_tool(self, tool_name):
        """Выбор инструмента"""
        if tool_name == "brush":
            self.canvas.current_tool = BrushTool()
            self.tool_label.setText("Инструмент: Кисть")
            logger.info("Выбран инструмент: Кисть")
        elif tool_name == "line":
            self.canvas.current_tool = LineTool()
            self.tool_label.setText("Инструмент: Линия")
            logger.info("Выбран инструмент: Линия")
        elif tool_name == "eraser":
            self.canvas.current_tool = EraserTool()
            self.tool_label.setText("Инструмент: Ластик")
            logger.info("Выбран инструмент: Ластик")