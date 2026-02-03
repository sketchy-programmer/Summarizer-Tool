import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import pyperclip
import sys
import subprocess
import os
from utils import resource_path
from summarizer import summarize_text, paraphrase_text, summarize_code


class FloatingPen(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Shortify")
        self.geometry("100x100")
        self.overrideredirect(True)  # Remove window decorations
        self.attributes("-topmost", True)  # Keep on top

        # Settings
        self.action_type = "summarize"
        self.min_length = 100
        self.max_length = 150
        self.writing_style = "default"
        self.language = None
        self.theme = "light"

        # Drag offset
        self.offset_x = 0
        self.offset_y = 0

        # Configure background
        self.configure(bg='#f0f0f0')

        # Main frame
        self.main_frame = tk.Frame(self, bg='#f0f0f0')
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Setup UI components
        self.setup_pen_icon()
        self.create_text_area()
        self.create_settings_panel()
        self.create_menu()

    def setup_pen_icon(self):
        """Setup the pen icon that users interact with."""
        try:
            image_path = resource_path("assets/pen.png")
            self.pen_image = Image.open(image_path).convert("RGBA")
            self.pen_image = self.pen_image.resize((80, 80), Image.Resampling.LANCZOS)
            self.pen_photo = ImageTk.PhotoImage(self.pen_image)

            self.pen_label = tk.Label(
                self.main_frame,
                image=self.pen_photo,
                bg='#f0f0f0',
                cursor="hand2"
            )
        except Exception as e:
            # Fallback if image not found
            self.pen_label = tk.Label(
                self.main_frame,
                text="✏️",
                font=('Arial', 40),
                bg='#f0f0f0',
                cursor="hand2"
            )

        self.pen_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Bind events
        self.pen_label.bind("<Button-1>", self.start_drag)
        self.pen_label.bind("<B1-Motion>", self.drag)
        self.pen_label.bind("<Button-2>", self.on_right_click)  # macOS right-click
        self.pen_label.bind("<Button-3>", self.on_right_click)  # Standard right-click
        self.pen_label.bind("<Control-Button-1>", self.on_right_click)  # Ctrl+click on macOS

    def create_text_area(self):
        """Create the expandable text area for results."""
        self.text_frame = tk.Frame(self.main_frame, bg='#f5f5f5')

        self.text_area = tk.Text(
            self.text_frame,
            height=12,
            width=45,
            wrap=tk.WORD,
            font=('Helvetica', 11),
            bg='#f5f5f5',
            fg='#333333',
            padx=10,
            pady=10,
            relief="flat",
            borderwidth=1
        )

        self.text_scroll = ttk.Scrollbar(
            self.text_frame,
            orient="vertical",
            command=self.text_area.yview
        )
        self.text_area.configure(yscrollcommand=self.text_scroll.set)

        # Don't pack yet - will show when needed

    def create_settings_panel(self):
        """Create the settings panel."""
        self.settings_frame = tk.Frame(self.main_frame, bg='#f5f5f5')

        # Action Type
        tk.Label(self.settings_frame, text="Action:", bg='#f5f5f5').grid(row=0, column=0, sticky="w", pady=5, padx=10)
        self.action_var = tk.StringVar(value="summarize")
        action_combo = ttk.Combobox(
            self.settings_frame,
            textvariable=self.action_var,
            values=["summarize", "paraphrase", "code_summarize"],
            state="readonly",
            width=15
        )
        action_combo.grid(row=0, column=1, pady=5, padx=10)

        # Style
        tk.Label(self.settings_frame, text="Style:", bg='#f5f5f5').grid(row=1, column=0, sticky="w", pady=5, padx=10)
        self.style_var = tk.StringVar(value="default")
        style_combo = ttk.Combobox(
            self.settings_frame,
            textvariable=self.style_var,
            values=["default", "academic", "casual", "business", "creative"],
            state="readonly",
            width=15
        )
        style_combo.grid(row=1, column=1, pady=5, padx=10)

        # Min Length
        tk.Label(self.settings_frame, text="Min Length:", bg='#f5f5f5').grid(row=2, column=0, sticky="w", pady=5, padx=10)
        self.min_length_var = tk.StringVar(value="100")
        min_entry = ttk.Entry(self.settings_frame, textvariable=self.min_length_var, width=10)
        min_entry.grid(row=2, column=1, sticky="w", pady=5, padx=10)

        # Max Length
        tk.Label(self.settings_frame, text="Max Length:", bg='#f5f5f5').grid(row=3, column=0, sticky="w", pady=5, padx=10)
        self.max_length_var = tk.StringVar(value="150")
        max_entry = ttk.Entry(self.settings_frame, textvariable=self.max_length_var, width=10)
        max_entry.grid(row=3, column=1, sticky="w", pady=5, padx=10)

        # Apply button
        apply_btn = ttk.Button(self.settings_frame, text="Apply", command=self.apply_settings)
        apply_btn.grid(row=4, column=0, columnspan=2, pady=15)

    def create_menu(self):
        """Create the right-click context menu."""
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="✨ Summarize", command=lambda: self.process_action("summarize"))
        self.menu.add_command(label="🔁 Paraphrase", command=lambda: self.process_action("paraphrase"))
        self.menu.add_command(label="💻 Code Summarize", command=lambda: self.process_action("code_summarize"))
        self.menu.add_separator()
        self.menu.add_command(label="⚙️ Settings", command=self.show_settings)
        self.menu.add_command(label="🎯 Hide Result", command=self.hide_panels)
        self.menu.add_separator()
        self.menu.add_command(label="❌ Quit", command=self.destroy)

    def on_right_click(self, event):
        """Show context menu on right-click."""
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    def start_drag(self, event):
        """Start dragging the window."""
        self.offset_x = event.x
        self.offset_y = event.y

    def drag(self, event):
        """Drag the window."""
        x = self.winfo_pointerx() - self.offset_x
        y = self.winfo_pointery() - self.offset_y
        self.geometry(f"+{x}+{y}")

    def process_action(self, action_type):
        """Process the selected action."""
        self.action_type = action_type

        # Try to copy selected text on macOS
        if sys.platform == "darwin":
            try:
                subprocess.run([
                    "osascript", "-e",
                    'tell application "System Events" to keystroke "c" using {command down}'
                ], check=False, timeout=1)
                self.after(300, self.process_clipboard)
            except Exception:
                self.after(100, self.process_clipboard)
        else:
            self.after(100, self.process_clipboard)

    def process_clipboard(self):
        """Process text from clipboard."""
        try:
            selected_text = pyperclip.paste()
        except Exception as e:
            self.show_result(f"Clipboard Error: {str(e)}")
            return

        if not selected_text or not selected_text.strip():
            self.show_result("No text in clipboard!\n\nCopy some text first (Cmd+C), then try again.")
            return

        # Show processing message
        self.show_result("Processing...")
        self.update()

        # Process based on action type
        try:
            if self.action_type == "summarize":
                result = summarize_text(
                    selected_text,
                    max_length=self.max_length,
                    min_length=self.min_length,
                    style=self.writing_style
                )
                title = f"📝 Summary ({self.writing_style})"
            elif self.action_type == "paraphrase":
                result = paraphrase_text(
                    selected_text,
                    max_length=self.max_length,
                    min_length=self.min_length,
                    style=self.writing_style
                )
                title = f"🔄 Paraphrase ({self.writing_style})"
            else:  # code_summarize
                result = summarize_code(
                    selected_text,
                    max_length=self.max_length,
                    language=self.language
                )
                title = "💻 Code Summary"

            self.show_result(f"{title}:\n\n{result}")

        except Exception as e:
            self.show_result(f"Error: {str(e)}")

    def show_result(self, text):
        """Show the result in the expandable text area."""
        # Hide settings if visible
        self.settings_frame.pack_forget()

        # Show text area
        self.text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.text_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Resize window
        self.geometry("400x350")

        # Insert text
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, text)

    def show_settings(self):
        """Show the settings panel."""
        # Hide text area
        self.text_frame.pack_forget()

        # Show settings
        self.settings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Resize window
        self.geometry("280x220")

    def apply_settings(self):
        """Apply settings and hide panel."""
        try:
            self.action_type = self.action_var.get()
            self.writing_style = self.style_var.get()
            self.min_length = int(self.min_length_var.get())
            self.max_length = int(self.max_length_var.get())

            # Validation
            if self.min_length < 50:
                self.min_length = 50
                self.min_length_var.set("50")
            if self.max_length < self.min_length:
                self.max_length = self.min_length + 50
                self.max_length_var.set(str(self.max_length))

        except ValueError:
            pass

        self.hide_panels()

    def hide_panels(self):
        """Hide all panels and return to icon view."""
        self.text_frame.pack_forget()
        self.settings_frame.pack_forget()
        self.geometry("100x100")


if __name__ == "__main__":
    app = FloatingPen()
    app.mainloop()
