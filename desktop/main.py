import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from pen_floating import FloatingPen

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FloatingPen()
    window.show()
    # ensure always-on-top (optional)
    window.setWindowFlag(Qt.WindowStaysOnTopHint, True)
    sys.exit(app.exec_())
