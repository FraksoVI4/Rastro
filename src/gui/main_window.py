from PyQt6.QtWidgets import (QMainWindow, QToolBar, QStatusBar, QSizePolicy, 
                             QPushButton, QMenu, QDialog, QVBoxLayout, QHBoxLayout,
                             QLabel, QScrollArea, QWidget, QSlider, QDialogButtonBox, 
                             QSpinBox, QColorDialog, QFileDialog, QSystemTrayIcon)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QColor, QPixmap, QIcon
from .canvas import Canvas
from tools.brush import BrushTool
from tools.eraser import EraserTool
from tools.line import LineTool
from tools.fill import FillTool
import logging
import os

logger = logging.getLogger(__name__)

class ColorButton(QPushButton):
    def __init__(self, initial_color=QColor(0, 0, 0), parent=None):
        super().__init__(parent)
        self.color = initial_color
        self.update_button_color()
    
    def update_button_color(self):
        pixmap = QPixmap(50, 20)
        pixmap.fill(self.color)
        self.setIcon(QIcon(pixmap))
        self.setIconSize(pixmap.size())
        
        self.setStyleSheet(f"""
            QPushButton {{ 
                background-color: {self.color.name()}; 
                border: 1px solid gray;
                border-radius: 3px;
            }}
            QPushButton:hover {{
                border: 2px solid black;
            }}
        """)

class ResizeDialog(QDialog):
    def __init__(self, current_width, current_height, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Размер холста")
        
        layout = QVBoxLayout()
        
        size_layout = QHBoxLayout()
        
        width_layout = QVBoxLayout()
        width_layout.addWidget(QLabel("Ширина:"))
        self.width_spin = QSpinBox()
        self.width_spin.setRange(100, 3000)
        self.width_spin.setValue(current_width)
        width_layout.addWidget(self.width_spin)
        
        height_layout = QVBoxLayout()
        height_layout.addWidget(QLabel("Высота:"))
        self.height_spin = QSpinBox()
        self.height_spin.setRange(100, 3000)
        self.height_spin.setValue(current_height)
        height_layout.addWidget(self.height_spin)
        
        size_layout.addLayout(width_layout)
        size_layout.addLayout(height_layout)
        layout.addLayout(size_layout)
        
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

class MainWindow(QMainWindow):\
    
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setupShortcuts()
        
    def initUI(self):
        # Установка заголовка и размера окна
        self.setWindowTitle("Rastro")
        self.setGeometry(100, 100, 800, 600)

        # Установка иконки приложения (для панели задач и заголовка окна)
        icon_path = os.path.abspath("src/gui/app-icon.png")  # Используйте .ico для Windows
        if not QIcon(icon_path).isNull():
            self.setWindowIcon(QIcon(icon_path))
        else:
            logger.error(f"Не удалось загрузить иконку по пути: {icon_path}")

        # Инициализация холста
        self.canvas = Canvas()

        # Создаем область прокрутки для холста
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.canvas)
        scroll_area.setWidgetResizable(False)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setCentralWidget(scroll_area)

        # Настройка статус-бара
        self.statusBar = QStatusBar()
        self.tool_label = QLabel("Инструмент: Кисть")
        self.size_label = QLabel(f"Размер холста: {self.canvas.width()}x{self.canvas.height()}")
        self.statusBar.addPermanentWidget(self.tool_label)
        self.statusBar.addPermanentWidget(self.size_label)
        self.setStatusBar(self.statusBar)

        # Создание панели инструментов
        self.createToolBar()

        # Добавление системного трея (если требуется)
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self)
            self.tray_icon.setIcon(QIcon(icon_path))
            tray_menu = QMenu()
            quit_action = QAction("Выход", self)
            quit_action.triggered.connect(self.close)
            tray_menu.addAction(quit_action)
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.show()
            logger.info("Иконка добавлена в системный трей.")
        else:
            logger.warning("Системный трей недоступен.")

        logger.info("Главное окно инициализировано")

    def createToolBar(self):
        """Создание панели инструментов"""
        toolbar = QToolBar()
        toolbar.setStyleSheet(f"""
            QToolBar {{
                background-color: palette(window);
                border-bottom: 1px solid palette(shadow);
                padding: 5px;
            }}
            QPushButton {{
                min-width: 60px;
                padding: 5px;
                margin: 2px;
                border-radius: 4px;
                background-color: palette(button);
                color: palette(button-text);
                border: 1px solid palette(mid);
            }}
            QPushButton:hover {{
                background-color: palette(light);
            }}
            QPushButton:pressed {{
                background-color: palette(dark);
                color: palette(bright-text);
            }}
        """)
        self.addToolBar(toolbar)

        # Кнопки отмены/повтора (маленькие)
        undo_btn = QPushButton("↶")
        undo_btn.setMaximumWidth(30)
        undo_btn.clicked.connect(self.canvas.undo)
        toolbar.addWidget(undo_btn)

        redo_btn = QPushButton("↷")
        redo_btn.setMaximumWidth(30)
        redo_btn.clicked.connect(self.canvas.redo)
        toolbar.addWidget(redo_btn)

        toolbar.addSeparator()

        # Инструменты
        tools = [
            ("Заливка", lambda: self.select_tool("fill")),
            ("Кисть", lambda: self.select_tool("brush")),
            ("Линия", lambda: self.select_tool("line")),
            ("Ластик", lambda: self.select_tool("eraser"))
        ]

        for name, action in tools:
            btn = QPushButton(name)
            btn.clicked.connect(action)
            toolbar.addWidget(btn)

        toolbar.addSeparator()

        # Кнопки настроек
        size_btn = QPushButton("Размер")
        size_btn.clicked.connect(self.show_size_dialog)
        toolbar.addWidget(size_btn)

        self.color_btn = ColorButton(self.canvas.color)
        self.color_btn.clicked.connect(self.show_color_dialog)
        toolbar.addWidget(self.color_btn)

    def setupShortcuts(self):
        # Существующие шорткаты для инструментов
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

        # Новые хоткеи для сохранения и открытия
        save_action = QAction('Сохранить', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_file)
        self.addAction(save_action)

        open_action = QAction('Открыть', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.load_file)
        self.addAction(open_action)

    def select_tool(self, tool_name):
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
        elif tool_name == "fill":
            self.canvas.current_tool = FillTool()
            self.tool_label.setText("Инструмент: Заливка")
            logger.info("Выбран инструмент: Заливка")

    def show_resize_dialog(self):
        dialog = ResizeDialog(self.canvas.width(), self.canvas.height(), self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            width, height = dialog.get_size()
            self.canvas.change_size(width, height)
            self.size_label.setText(f"Размер холста: {width}x{height}")
            logger.info(f"Изменен размер холста на {width}x{height}")

    def show_size_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Размер инструмента")
        
        layout = QVBoxLayout(dialog)
        
        size_layout = QHBoxLayout()
        size_label = QLabel("Размер:")
        size_layout.addWidget(size_label)
        
        size_slider = QSlider(Qt.Orientation.Horizontal)
        size_slider.setMinimum(1)
        size_slider.setMaximum(50)
        size_slider.setValue(self.canvas.brush_size)
        size_layout.addWidget(size_slider)
        
        size_value_label = QLabel(str(self.canvas.brush_size))
        size_layout.addWidget(size_value_label)
        
        layout.addLayout(size_layout)
        
        def update_size_label(value):
            size_value_label.setText(str(value))
        
        size_slider.valueChanged.connect(update_size_label)
        
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        
        def accept():
            self.canvas.brush_size = size_slider.value()
            dialog.accept()
        
        button_box.accepted.connect(accept)
        button_box.rejected.connect(dialog.reject)
        
        layout.addWidget(button_box)
        
        dialog.exec()

    def show_color_dialog(self):
        color = QColorDialog.getColor(self.canvas.color, self, "Выбор цвета")
        
        if color.isValid():
            self.canvas.color = color
            
            self.color_btn.color = color
            self.color_btn.update_button_color()
            
            logger.info(f"Выбран новый цвет: RGB({color.red()}, {color.green()}, {color.blue()})")
            self.statusBar.showMessage(f"Цвет изменен", 2000)

    def save_file(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, 
            "Сохранить изображение", 
            "", 
            "Изображения (*.png *.jpg *.bmp)"
        )
        if filename:
            self.canvas.save_image(filename)
            logger.info(f"Изображение сохранено: {filename}")
            self.statusBar.showMessage(f"Сохранено в {filename}", 2000)

    def load_file(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, 
            "Открыть изображение", 
            "", 
            "Изображения (*.png *.jpg *.bmp)"
        )
        if filename:
            self.canvas.load_image(filename)
            logger.info(f"Изображение загружено: {filename}")
            self.statusBar.showMessage(f"Загружено из {filename}", 2000)

    def save_file_as(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, 
            "Сохранить изображение как", 
            "", 
            "Изображения (*.png *.jpg *.bmp)"
        )
        if filename:
            self.canvas.save_image(filename)
            logger.info(f"Изображение сохранено как: {filename}")
            self.statusBar.showMessage(f"Сохранено как {filename}", 2000)