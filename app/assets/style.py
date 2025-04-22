"""
Stylesheet chung cho toàn bộ ứng dụng Attendance Management
"""

STYLE = """
/* Main Application Style */
QMainWindow, QDialog {
    background-color: #f5f5f7;
}

/* Widget Styles */
QWidget {
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 10pt;
    color: #333;
}

/* Label Styles */
QLabel {
    color: #333;
    padding: 2px;
}

QLabel[title="true"] {
    font-size: 18pt;
    font-weight: bold;
    color: #1a73e8;
    padding: 10px;
}

QLabel[subtitle="true"] {
    font-size: 14pt;
    font-weight: bold;
    color: #444;
    padding: 6px;
}

QLabel[header="true"] {
    font-size: 12pt;
    font-weight: bold;
    color: #555;
    padding: 4px;
}

/* Button Styles */
QPushButton {
    background-color: #1a73e8;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: bold;
    min-width: 80px;
}

QPushButton:hover {
    background-color: #4285f4;
}

QPushButton:pressed {
    background-color: #0d47a1;
}

QPushButton:disabled {
    background-color: #cccccc;
    color: #666666;
}

QPushButton[danger="true"] {
    background-color: #ef5350;
}

QPushButton[danger="true"]:hover {
    background-color: #e53935;
}

QPushButton[secondary="true"] {
    background-color: #78909c;
}

QPushButton[secondary="true"]:hover {
    background-color: #607d8b;
}

/* Input Field Styles */
QLineEdit, QDateEdit, QComboBox {
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 8px;
    background-color: white;
    selection-background-color: #cce5ff;
}

QLineEdit:focus, QDateEdit:focus, QComboBox:focus {
    border: 2px solid #1a73e8;
}

/* Table Styles */
QTableWidget {
    alternate-background-color: #f9f9f9;
    gridline-color: #ddd;
    selection-background-color: #cce5ff;
    selection-color: #333;
    border: 1px solid #ddd;
    border-radius: 4px;
}

QTableWidget::item {
    padding: 6px;
}

QTableWidget::item:selected {
    background-color: #cce5ff;
    color: #333;
}

QHeaderView::section {
    background-color: #f0f0f0;
    color: #444;
    padding: 6px;
    border: none;
    border-right: 1px solid #ddd;
    border-bottom: 1px solid #ddd;
    font-weight: bold;
}

/* Tab Widget Styles */
QTabWidget::pane {
    border: 1px solid #ddd;
    border-radius: 4px;
    background-color: white;
}

QTabBar::tab {
    background-color: #f0f0f0;
    color: #333;
    padding: 8px 16px;
    margin-right: 2px;
    border-top-left-radius: 4px;
    border-top-right-radius:.4px;
}

QTabBar::tab:selected {
    background-color: #1a73e8;
    color: white;
}

QTabBar::tab:hover:!selected {
    background-color: #e0e0e0;
}

/* Scrollbar Styles */
QScrollBar:vertical {
    border: none;
    background-color: #f5f5f7;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #c0c0c0;
    border-radius: 4px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #a0a0a0;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    border: none;
    background-color: #f5f5f7;
    height: 8px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background-color: #c0c0c0;
    border-radius: 4px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #a0a0a0;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* Menu Styles */
QMenuBar {
    background-color: #f5f5f7;
    color: #333;
}

QMenuBar::item {
    padding: 6px 12px;
    background-color: transparent;
}

QMenuBar::item:selected {
    background-color: #e0e0e0;
}

QMenu {
    background-color: white;
    border: 1px solid #ddd;
}

QMenu::item {
    padding: 6px 24px 6px 12px;
}

QMenu::item:selected {
    background-color: #cce5ff;
    color: #333;
}

/* Form Layout Styles */
QFormLayout {
    spacing: 12px;
}

/* Status Bar Styles */
QStatusBar {
    background-color: #f5f5f7;
    color: #555;
}

/* Group Box Styles */
QGroupBox {
    border: 1px solid #ddd;
    border-radius: 4px;
    margin-top: 12px;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 0 5px;
}
"""