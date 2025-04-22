import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget

def test_pyqt():
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("PyQt5 Test")
    window.setGeometry(100, 100, 300, 200)
    label = QLabel("PyQt5 is working!", window)
    label.move(100, 80)
    window.show()
    return app.exec_()

if __name__ == "__main__":
    test_pyqt()