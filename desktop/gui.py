import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import pyperclip
import sys
import subprocess
import os
from utils import resource_path
from summarizer import summarize_text, paraphrase_text, summarize_code


# Color scheme
COLORS = {
    'primary': '#6366f1',      # Indigo
    'primary_dark': '#4f46e5',
    'secondary': '#8b5cf6',    # Purple
    'background': '#ffffff',
    'surface': '#f8fafc',
    'text': '#1e293b',
    'text_light': '#64748b',
    'border': '#e2e8f0',
    'success': '#22c55e',
    'error': '#ef4444',
}


class FloatingPen(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Shortify")
        self.geometry("80x80")
        self.overrideredirect(True)
        self.attributes("-topmost", True)

        # Settings
        self.action_type = "summarize"
        self.min_length = 100
        self.max_length = 150
        self.writing_style = "default"
        self.language = None

        # Drag offset
        self.offset_x = 0
        self.offset_y = 0

        # Transparent background
        self.transparent_color = '#010101'
        self.configure(bg=self.transparent_color)

        if sys.platform == "darwin":
            self.attributes('-transparent', True)
            self.config(bg='systemTransparent')
            self.transparent_color = 'systemTransparent'
        else:
            self.attributes('-transparentcolor', self.transparent_color)

        # Configure styles
        self.setup_styles()

        # Main frame
        self.main_frame = tk.Frame(self, bg=self.transparent_color)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Setup UI
        self.setup_pen_icon()
        self.create_result_panel()
        self.create_settings_panel()
        self.create_menu()

    def setup_styles(self):
        """Configure ttk styles for modern look."""
        style = ttk.Style()
        style.theme_use('clam')

        # Combobox style
        style.configure('Modern.TCombobox',
            fieldbackground=COLORS['background'],
            background=COLORS['background'],
            foreground=COLORS['text'],
            borderwidth=1,
            relief='flat',
            padding=5
        )

        # Entry style
        style.configure('Modern.TEntry',
            fieldbackground=COLORS['background'],
            foreground=COLORS['text'],
            borderwidth=1,
            relief='flat',
            padding=5
        )

        # Button styles
        style.configure('Primary.TButton',
            background=COLORS['primary'],
            foreground='white',
            borderwidth=0,
            padding=(20, 10),
            font=('Helvetica', 11, 'bold')
        )
        style.map('Primary.TButton',
            background=[('active', COLORS['primary_dark'])]
        )

        style.configure('Secondary.TButton',
            background=COLORS['border'],
            foreground=COLORS['text'],
            borderwidth=0,
            padding=(15, 8),
            font=('Helvetica', 10)
        )

    def setup_pen_icon(self):
        """Setup the pen icon."""
        image_path = resource_path("assets/pen.png")
        print(f"Looking for pen.png at: {image_path}")
        print(f"File exists: {os.path.exists(image_path)}")

        try:
            if os.path.exists(image_path):
                self.pen_image = Image.open(image_path).convert("RGBA")
                self.pen_image = self.pen_image.resize((70, 70), Image.Resampling.LANCZOS)
                self.pen_photo = ImageTk.PhotoImage(self.pen_image)

                self.pen_label = tk.Label(
                    self.main_frame,
                    image=self.pen_photo,
                    bg=self.transparent_color,
                    borderwidth=0,
                    highlightthickness=0,
                    cursor="hand2"
                )
                print("Pen image loaded successfully!")
            else:
                raise FileNotFoundError(f"pen.png not found at {image_path}")
        except Exception as e:
            print(f"Error loading pen image: {e}")
            # Fallback to emoji
            self.pen_label = tk.Label(
                self.main_frame,
                text="✏️",
                font=('Arial', 40),
                bg=self.transparent_color,
                cursor="hand2"
            )

        self.pen_label.pack(fill=tk.BOTH, expand=True)

        # Bind events
        self.pen_label.bind("<Button-1>", self.start_drag)
        self.pen_label.bind("<B1-Motion>", self.drag)
        self.pen_label.bind("<Button-2>", self.on_right_click)
        self.pen_label.bind("<Button-3>", self.on_right_click)
        self.pen_label.bind("<Control-Button-1>", self.on_right_click)

    def create_result_panel(self):
        """Create the result display panel."""
        self.result_frame = tk.Frame(self.main_frame, bg=COLORS['background'])

        # Header with title and close button
        header = tk.Frame(self.result_frame, bg=COLORS['primary'], height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        self.result_title = tk.Label(
            header,
            text="✨ Result",
            font=('Helvetica', 14, 'bold'),
            bg=COLORS['primary'],
            fg='white',
            padx=15
        )
        self.result_title.pack(side=tk.LEFT, pady=12)

        # Close button
        close_btn = tk.Label(
            header,
            text="✕",
            font=('Helvetica', 16),
            bg=COLORS['primary'],
            fg='white',
            cursor="hand2",
            padx=15
        )
        close_btn.pack(side=tk.RIGHT, pady=10)
        close_btn.bind("<Button-1>", lambda e: self.hide_panels())

        # Text area container
        text_container = tk.Frame(self.result_frame, bg=COLORS['background'], padx=15, pady=15)
        text_container.pack(fill=tk.BOTH, expand=True)

        self.text_area = tk.Text(
            text_container,
            wrap=tk.WORD,
            font=('Helvetica', 12),
            bg=COLORS['surface'],
            fg=COLORS['text'],
            padx=15,
            pady=15,
            relief='flat',
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=COLORS['border'],
            highlightcolor=COLORS['primary']
        )

        self.text_scroll = ttk.Scrollbar(text_container, orient="vertical", command=self.text_area.yview)
        self.text_area.configure(yscrollcommand=self.text_scroll.set)

        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.text_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Copy button at bottom
        btn_frame = tk.Frame(self.result_frame, bg=COLORS['background'], pady=10)
        btn_frame.pack(fill=tk.X)

        copy_btn = tk.Button(
            btn_frame,
            text="📋 Copy to Clipboard",
            font=('Helvetica', 11),
            bg=COLORS['primary'],
            fg='white',
            activebackground=COLORS['primary_dark'],
            activeforeground='white',
            relief='flat',
            padx=20,
            pady=8,
            cursor="hand2",
            command=self.copy_result
        )
        copy_btn.pack()

    def create_settings_panel(self):
        """Create an enhanced settings panel."""
        self.settings_frame = tk.Frame(self.main_frame, bg=COLORS['background'])

        # Header
        header = tk.Frame(self.settings_frame, bg=COLORS['secondary'], height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="⚙️ Settings",
            font=('Helvetica', 14, 'bold'),
            bg=COLORS['secondary'],
            fg='white',
            padx=15
        ).pack(side=tk.LEFT, pady=12)

        # Close button
        close_btn = tk.Label(
            header,
            text="✕",
            font=('Helvetica', 16),
            bg=COLORS['secondary'],
            fg='white',
            cursor="hand2",
            padx=15
        )
        close_btn.pack(side=tk.RIGHT, pady=10)
        close_btn.bind("<Button-1>", lambda e: self.hide_panels())

        # Settings content
        content = tk.Frame(self.settings_frame, bg=COLORS['background'], padx=20, pady=20)
        content.pack(fill=tk.BOTH, expand=True)

        # Action Type
        self.create_setting_row(content, 0, "Action", "action")
        self.action_var = tk.StringVar(value="summarize")
        action_combo = ttk.Combobox(
            content,
            textvariable=self.action_var,
            values=["summarize", "paraphrase", "code_summarize"],
            state="readonly",
            width=18,
            style='Modern.TCombobox'
        )
        action_combo.grid(row=0, column=1, pady=8, padx=5, sticky="ew")

        # Style
        self.create_setting_row(content, 1, "Style", "style")
        self.style_var = tk.StringVar(value="default")
        style_combo = ttk.Combobox(
            content,
            textvariable=self.style_var,
            values=["default", "academic", "casual", "business", "creative"],
            state="readonly",
            width=18,
            style='Modern.TCombobox'
        )
        style_combo.grid(row=1, column=1, pady=8, padx=5, sticky="ew")

        # Min Length
        self.create_setting_row(content, 2, "Min Words", "min")
        self.min_length_var = tk.StringVar(value="100")
        min_entry = ttk.Entry(content, textvariable=self.min_length_var, width=20, style='Modern.TEntry')
        min_entry.grid(row=2, column=1, pady=8, padx=5, sticky="ew")

        # Max Length
        self.create_setting_row(content, 3, "Max Words", "max")
        self.max_length_var = tk.StringVar(value="150")
        max_entry = ttk.Entry(content, textvariable=self.max_length_var, width=20, style='Modern.TEntry')
        max_entry.grid(row=3, column=1, pady=8, padx=5, sticky="ew")

        # Configure grid
        content.columnconfigure(1, weight=1)

        # Buttons frame
        btn_frame = tk.Frame(self.settings_frame, bg=COLORS['background'], pady=15)
        btn_frame.pack(fill=tk.X)

        apply_btn = tk.Button(
            btn_frame,
            text="✓ Apply Settings",
            font=('Helvetica', 11, 'bold'),
            bg=COLORS['primary'],
            fg='white',
            activebackground=COLORS['primary_dark'],
            activeforeground='white',
            relief='flat',
            padx=25,
            pady=10,
            cursor="hand2",
            command=self.apply_settings
        )
        apply_btn.pack()

    def create_setting_row(self, parent, row, label_text, icon_type):
        """Create a styled setting row with label."""
        icons = {
            "action": "🎯",
            "style": "🎨",
            "min": "📏",
            "max": "📐"
        }

        label_frame = tk.Frame(parent, bg=COLORS['background'])
        label_frame.grid(row=row, column=0, sticky="w", pady=8)

        tk.Label(
            label_frame,
            text=icons.get(icon_type, "•"),
            font=('Helvetica', 12),
            bg=COLORS['background'],
            fg=COLORS['primary']
        ).pack(side=tk.LEFT)

        tk.Label(
            label_frame,
            text=f" {label_text}",
            font=('Helvetica', 12),
            bg=COLORS['background'],
            fg=COLORS['text']
        ).pack(side=tk.LEFT)

    def create_menu(self):
        """Create the right-click context menu."""
        self.menu = tk.Menu(self, tearoff=0, font=('Helvetica', 11))
        self.menu.configure(bg=COLORS['background'], fg=COLORS['text'], activebackground=COLORS['primary'], activeforeground='white')

        self.menu.add_command(label="  ✨  Summarize", command=lambda: self.process_action("summarize"))
        self.menu.add_command(label="  🔁  Paraphrase", command=lambda: self.process_action("paraphrase"))
        self.menu.add_command(label="  💻  Code Summarize", command=lambda: self.process_action("code_summarize"))
        self.menu.add_separator()
        self.menu.add_command(label="  ⚙️  Settings", command=self.show_settings)
        self.menu.add_command(label="  🎯  Hide", command=self.hide_panels)
        self.menu.add_separator()
        self.menu.add_command(label="  ❌  Quit", command=self.destroy)

    def on_right_click(self, event):
        """Show context menu."""
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    def start_drag(self, event):
        """Start dragging."""
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
            self.show_result(f"Clipboard Error: {str(e)}", error=True)
            return

        if not selected_text or not selected_text.strip():
            self.show_result("No text in clipboard!\n\nCopy some text first (Cmd+C), then try again.", error=True)
            return

        self.show_result("⏳ Processing...", title="Please wait")
        self.update()

        try:
            if self.action_type == "summarize":
                result = summarize_text(
                    selected_text,
                    max_length=self.max_length,
                    min_length=self.min_length,
                    style=self.writing_style
                )
                self.show_result(result, title="✨ Summary")
            elif self.action_type == "paraphrase":
                result = paraphrase_text(
                    selected_text,
                    max_length=self.max_length,
                    min_length=self.min_length,
                    style=self.writing_style
                )
                self.show_result(result, title="🔁 Paraphrase")
            else:
                result = summarize_code(
                    selected_text,
                    max_length=self.max_length,
                    language=self.language
                )
                self.show_result(result, title="💻 Code Summary")

        except Exception as e:
            self.show_result(f"Error: {str(e)}", error=True)

    def show_result(self, text, title="✨ Result", error=False):
        """Show the result panel."""
        self.settings_frame.pack_forget()

        self.config(bg=COLORS['background'])
        self.main_frame.config(bg=COLORS['background'])

        # Update title
        color = COLORS['error'] if error else COLORS['primary']
        self.result_title.config(text=title, bg=color)
        self.result_title.master.config(bg=color)

        # Update close button background
        for widget in self.result_title.master.winfo_children():
            if isinstance(widget, tk.Label) and widget != self.result_title:
                widget.config(bg=color)

        self.result_frame.pack(fill=tk.BOTH, expand=True)
        self.geometry("420x380")

        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, text)

    def show_settings(self):
        """Show the settings panel."""
        self.result_frame.pack_forget()

        self.config(bg=COLORS['background'])
        self.main_frame.config(bg=COLORS['background'])

        self.settings_frame.pack(fill=tk.BOTH, expand=True)
        self.geometry("320x320")

    def apply_settings(self):
        """Apply settings."""
        try:
            self.action_type = self.action_var.get()
            self.writing_style = self.style_var.get()
            self.min_length = int(self.min_length_var.get())
            self.max_length = int(self.max_length_var.get())

            if self.min_length < 50:
                self.min_length = 50
                self.min_length_var.set("50")
            if self.max_length < self.min_length:
                self.max_length = self.min_length + 50
                self.max_length_var.set(str(self.max_length))
        except ValueError:
            pass

        self.hide_panels()

    def copy_result(self):
        """Copy result to clipboard."""
        text = self.text_area.get(1.0, tk.END).strip()
        if text:
            pyperclip.copy(text)

    def hide_panels(self):
        """Hide all panels."""
        self.result_frame.pack_forget()
        self.settings_frame.pack_forget()
        self.geometry("80x80")

        if sys.platform == "darwin":
            self.config(bg='systemTransparent')
            self.main_frame.config(bg='systemTransparent')
            self.pen_label.config(bg='systemTransparent')
        else:
            self.config(bg=self.transparent_color)
            self.main_frame.config(bg=self.transparent_color)
            self.pen_label.config(bg=self.transparent_color)


if __name__ == "__main__":
    app = FloatingPen()
    app.mainloop()
