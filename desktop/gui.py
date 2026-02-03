import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip
import sys
import subprocess
from summarizer import summarize_text, paraphrase_text, summarize_code
from config import get_api_key

class FloatingPen(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Shortify")
        self.geometry("300x400")

        # Keep window on top
        self.attributes("-topmost", True)

        # Settings
        self.action_type = "summarize"
        self.min_length = 100
        self.max_length = 150
        self.writing_style = "default"
        self.language = None

        # Create main UI
        self.create_ui()

    def create_ui(self):
        # Title
        title_label = tk.Label(self, text="Shortify", font=('Helvetica', 18, 'bold'))
        title_label.pack(pady=10)

        # Action buttons frame
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        summarize_btn = tk.Button(
            btn_frame,
            text="✨ Summarize",
            command=lambda: self.process_action("summarize"),
            width=20,
            height=2
        )
        summarize_btn.pack(pady=5)

        paraphrase_btn = tk.Button(
            btn_frame,
            text="🔁 Paraphrase",
            command=lambda: self.process_action("paraphrase"),
            width=20,
            height=2
        )
        paraphrase_btn.pack(pady=5)

        code_btn = tk.Button(
            btn_frame,
            text="💻 Code Summarize",
            command=lambda: self.process_action("code_summarize"),
            width=20,
            height=2
        )
        code_btn.pack(pady=5)

        # Result text area
        self.text_area = tk.Text(
            self,
            height=10,
            width=35,
            wrap=tk.WORD,
            font=('Helvetica', 11),
            bg='#f5f5f5',
            fg='#333333'
        )
        self.text_area.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Status label
        self.status_label = tk.Label(self, text="Copy text, then click an action", fg='gray')
        self.status_label.pack(pady=5)

        # Quit button
        quit_btn = tk.Button(self, text="Quit", command=self.destroy, width=10)
        quit_btn.pack(pady=10)

    def process_action(self, action_type):
        self.action_type = action_type
        self.status_label.config(text="Processing...")
        self.update()

        # Get clipboard content
        try:
            selected_text = pyperclip.paste()
        except Exception as e:
            self.show_error(f"Clipboard error: {e}")
            return

        if not selected_text or not selected_text.strip():
            self.show_error("No text in clipboard! Copy some text first.")
            return

        # Process the text
        try:
            if self.action_type == "summarize":
                result = summarize_text(
                    selected_text,
                    max_length=self.max_length,
                    min_length=self.min_length,
                    style=self.writing_style
                )
                title = "Summary"
            elif self.action_type == "paraphrase":
                result = paraphrase_text(
                    selected_text,
                    max_length=self.max_length,
                    min_length=self.min_length,
                    style=self.writing_style
                )
                title = "Paraphrase"
            else:  # code_summarize
                result = summarize_code(
                    selected_text,
                    max_length=self.max_length,
                    language=self.language
                )
                title = "Code Summary"

            # Display result
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, f"{title}:\n\n{result}")
            self.status_label.config(text="Done!")

        except Exception as e:
            self.show_error(f"Error: {str(e)}")

    def show_error(self, message):
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, message)
        self.status_label.config(text="Error occurred")


if __name__ == "__main__":
    app = FloatingPen()
    app.mainloop()
