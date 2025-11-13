import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QMenu, QAction, QTextEdit, QVBoxLayout, QDialog, QFormLayout,
    QComboBox, QLineEdit, QPushButton, QScrollArea, QHBoxLayout
)
from PyQt5.QtGui import QPixmap, QCursor, QColor, QPalette
from PyQt5.QtCore import Qt, QPoint
import pyperclip
import subprocess
import time

# Placeholder imports for your summarizer logic
# from summarizer import summarize_text, paraphrase_text, summarize_code

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(300, 300)
        layout = QFormLayout(self)

        # Action type
        self.action_combo = QComboBox()
        self.action_combo.addItems(["summarize", "paraphrase", "code_summarize"])
        layout.addRow("Action:", self.action_combo)

        # Language
        self.language_combo = QComboBox()
        self.language_combo.addItems([
            "auto-detect", "python", "javascript", "java", "c++", "c#", "go", "ruby", "php",
            "swift", "typescript", "rust", "kotlin", "sql"
        ])
        layout.addRow("Language:", self.language_combo)

        # Style
        self.style_combo = QComboBox()
        self.style_combo.addItems(["default", "academic", "casual", "business", "creative"])
        layout.addRow("Style:", self.style_combo)

        # Min/Max length
        self.min_length_edit = QLineEdit("100")
        self.max_length_edit = QLineEdit("150")
        layout.addRow("Min Length:", self.min_length_edit)
        layout.addRow("Max Length:", self.max_length_edit)

        # Theme
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["light", "dark"])
        layout.addRow("Theme:", self.theme_combo)

        # Apply button
        self.apply_btn = QPushButton("Apply")
        layout.addRow(self.apply_btn)

        self.apply_btn.clicked.connect(self.accept)

    def get_settings(self):
        return {
            "action_type": self.action_combo.currentText(),
            "language": self.language_combo.currentText(),
            "writing_style": self.style_combo.currentText(),
            "min_length": self.min_length_edit.text(),
            "max_length": self.max_length_edit.text(),
            "theme": self.theme_combo.currentText()
        }

class FloatingPen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle("Shortify")

        # Settings
        self.action_type = "summarize"
        self.min_length = 100
        self.max_length = 150
        self.writing_style = "default"
        self.language = None
        self.theme = "light"

        # Layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Pen icon
        self.label = QLabel(self)
        pixmap = QPixmap("assets/pen.png")
        self.label.setPixmap(pixmap)
        self.label.setScaledContents(True)
        self.label.setFixedSize(100, 100)
        self.layout.addWidget(self.label, alignment=Qt.AlignCenter)

        # Text area (hidden by default)
        self.text_area = QTextEdit(self)
        self.text_area.setReadOnly(True)
        self.text_area.hide()
        self.layout.addWidget(self.text_area)

        # Dragging
        self.drag_position = None

        # Context menu
        self.menu = QMenu(self)
        self.menu.addAction("✨ Summarize", lambda: self.process_action("summarize"))
        self.menu.addAction("🔁 Paraphrase", lambda: self.process_action("paraphrase"))
        self.menu.addAction("💻 Code Summarize", lambda: self.process_action("code_summarize"))
        self.menu.addAction("⚙️ Settings", self.show_settings)
        self.menu.addAction("🎯 Hide", self.hide_text_area)
        self.menu.addAction("❌ Cancel", self.menu.close)
        self.menu.addAction("🚫 Stop", QApplication.quit)

        # Connect events
        self.label.setContextMenuPolicy(Qt.CustomContextMenu)
        self.label.customContextMenuRequested.connect(self.show_menu)
        self.label.mousePressEvent = self.mousePressEvent
        self.label.mouseMoveEvent = self.mouseMoveEvent
        self.label.mouseReleaseEvent = self.mouseReleaseEvent

        self.resize(100, 100)
        self.apply_theme()

    def show_menu(self, pos):
        self.menu.exec_(QCursor.pos())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
        elif event.button() == Qt.RightButton:
            self.show_menu(event.pos())

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_position = None

    def show_settings(self):
        dlg = SettingsDialog(self)
        # Set current values
        dlg.action_combo.setCurrentText(self.action_type)
        dlg.language_combo.setCurrentText(self.language or "auto-detect")
        dlg.style_combo.setCurrentText(self.writing_style)
        dlg.min_length_edit.setText(str(self.min_length))
        dlg.max_length_edit.setText(str(self.max_length))
        dlg.theme_combo.setCurrentText(self.theme)
        if dlg.exec_():
            settings = dlg.get_settings()
            self.action_type = settings["action_type"]
            self.language = settings["language"] if settings["language"] != "auto-detect" else None
            self.writing_style = settings["writing_style"]
            self.min_length = int(settings["min_length"])
            self.max_length = int(settings["max_length"])
            self.theme = settings["theme"]
            self.apply_theme()

    def apply_theme(self):
        if self.theme == "dark":
            palette = QPalette()
            palette.setColor(QPalette.Base, QColor("#1e1e1e"))
            palette.setColor(QPalette.Text, QColor("#ffffff"))
            self.text_area.setPalette(palette)
            self.text_area.setStyleSheet("background-color: #1e1e1e; color: #ffffff;")
        else:
            palette = QPalette()
            palette.setColor(QPalette.Base, QColor("#f5f5f5"))
            palette.setColor(QPalette.Text, QColor("#333333"))
            self.text_area.setPalette(palette)
            self.text_area.setStyleSheet("background-color: #f5f5f5; color: #333333;")

    def process_action(self, action_type):
        """
        Try to simulate Cmd/Ctrl+C then wait for the clipboard to change.
        On macOS this requires granting Accessibility permission to the host app.
        """
        import sys
        import subprocess
        import time

        self.action_type = action_type

        previous_clip = pyperclip.paste()

        # attempt to copy the current selection into the clipboard
        try:
            if sys.platform == "darwin":
                subprocess.run([
                    "osascript", "-e",
                    'tell application "System Events" to keystroke "c" using {command down}'
                ], check=False)
            elif sys.platform.startswith("win"):
                try:
                    import keyboard
                    keyboard.send("ctrl+c")
                except Exception:
                    pass
            else:
                try:
                    subprocess.run(["xdotool", "key", "ctrl+c"], check=False)
                except Exception:
                    pass
        except Exception:
            pass

        # wait for clipboard to update with retries
        selected_text = None
        for _ in range(8):  # ~8 attempts -> ~0.4s total
            time.sleep(0.05)
            selected_text = pyperclip.paste()
            if selected_text and selected_text != previous_clip:
                break

        # if clipboard didn't change, instruct user
        if not selected_text or selected_text == previous_clip:
            self.show_error(
                "No new selection copied. Select text, press Cmd+C manually (or grant Accessibility permission to Terminal/VSCode), then try Summarize again."
            )
            return

        # process text (placeholder logic)
        if selected_text.strip():
            if self.action_type == "summarize":
                result = f"Summary ({self.writing_style} style):\n\n{selected_text[:200]}..."
            elif self.action_type == "paraphrase":
                result = f"Paraphrase ({self.writing_style} style):\n\n{selected_text[:200]}..."
            else:
                result = f"Code Summary ({self.language or 'auto-detected'}):\n\n{selected_text[:200]}..."

            self.text_area.setText(result)
            self.text_area.show()
            self.resize(450, 350)
        else:
            self.show_error("No text selected!")

    def show_error(self, message):
        self.text_area.setText(f"Error: {message}")
        self.text_area.show()
        self.resize(400, 200)

    def hide_text_area(self):
        self.text_area.hide()
        self.resize(100, 100)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FloatingPen()
    window.show()
    window.setWindowFlag(Qt.WindowStaysOnTopHint, True)  # Ensure always on top
    sys.exit(app.exec_())