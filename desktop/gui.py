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
    'primary': '#6366f1',
    'primary_dark': '#4f46e5',
    'secondary': '#8b5cf6',
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

        # Settings
        self.action_type = "summarize"
        self.min_length = 100
        self.max_length = 150
        self.writing_style = "default"
        self.language = None

        # Drag offset
        self.offset_x = 0
        self.offset_y = 0

        # Keep reference to image
        self.pen_photo = None
        self.pen_label = None

        # Window setup - simple floating window
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.geometry("90x90")
        self.configure(bg='#f0f0f0')

        # Main frame
        self.main_frame = tk.Frame(self, bg='#f0f0f0')
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Setup styles
        self.setup_styles()

        # Create UI
        self.setup_pen_icon()
        self.create_result_panel()
        self.create_settings_panel()
        self.create_menu()

    def setup_styles(self):
        """Configure ttk styles."""
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except:
            pass

    def setup_pen_icon(self):
        """Setup the pen icon."""
        image_path = resource_path("assets/pen.png")

        try:
            if os.path.exists(image_path):
                # Load and resize image
                pil_image = Image.open(image_path).convert("RGBA")
                pil_image = pil_image.resize((70, 70), Image.Resampling.LANCZOS)

                # Create PhotoImage
                self.pen_photo = ImageTk.PhotoImage(pil_image)

                # Create label with image
                self.pen_label = tk.Label(
                    self.main_frame,
                    image=self.pen_photo,
                    bg='#f0f0f0',
                    cursor="hand2"
                )
            else:
                raise FileNotFoundError("pen.png not found")
        except Exception as e:
            print(f"Image load error: {e}")
            self.pen_label = tk.Label(
                self.main_frame,
                text="📝",
                font=('Arial', 35),
                bg='#f0f0f0',
                cursor="hand2"
            )

        self.pen_label.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Bind events
        self.pen_label.bind("<Button-1>", self.start_drag)
        self.pen_label.bind("<B1-Motion>", self.drag)
        self.pen_label.bind("<Button-2>", self.show_menu)
        self.pen_label.bind("<Button-3>", self.show_menu)
        self.pen_label.bind("<Control-Button-1>", self.show_menu)

    def create_result_panel(self):
        """Create result panel."""
        self.result_frame = tk.Frame(self.main_frame, bg=COLORS['background'])

        # Header
        header = tk.Frame(self.result_frame, bg=COLORS['primary'], height=45)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        self.result_title = tk.Label(
            header,
            text="✨ Result",
            font=('Helvetica', 13, 'bold'),
            bg=COLORS['primary'],
            fg='white'
        )
        self.result_title.pack(side=tk.LEFT, padx=15, pady=10)

        close_btn = tk.Label(
            header,
            text="✕",
            font=('Helvetica', 14, 'bold'),
            bg=COLORS['primary'],
            fg='white',
            cursor="hand2"
        )
        close_btn.pack(side=tk.RIGHT, padx=15, pady=10)
        close_btn.bind("<Button-1>", lambda e: self.hide_panels())

        # Text area
        text_frame = tk.Frame(self.result_frame, bg=COLORS['background'])
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.text_area = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=('Helvetica', 11),
            bg=COLORS['surface'],
            fg=COLORS['text'],
            padx=12,
            pady=12,
            relief='flat',
            highlightthickness=1,
            highlightbackground=COLORS['border']
        )

        scrollbar = ttk.Scrollbar(text_frame, command=self.text_area.yview)
        self.text_area.configure(yscrollcommand=scrollbar.set)

        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Copy button
        btn_frame = tk.Frame(self.result_frame, bg=COLORS['background'])
        btn_frame.pack(fill=tk.X, pady=10)

        copy_btn = tk.Button(
            btn_frame,
            text="📋 Copy",
            font=('Helvetica', 10),
            bg=COLORS['primary'],
            fg='white',
            relief='flat',
            padx=15,
            pady=5,
            cursor="hand2",
            command=self.copy_result
        )
        copy_btn.pack()

    def create_settings_panel(self):
        """Create settings panel."""
        self.settings_frame = tk.Frame(self.main_frame, bg=COLORS['background'])

        # Header
        header = tk.Frame(self.settings_frame, bg=COLORS['secondary'], height=45)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="⚙️ Settings",
            font=('Helvetica', 13, 'bold'),
            bg=COLORS['secondary'],
            fg='white'
        ).pack(side=tk.LEFT, padx=15, pady=10)

        close_btn = tk.Label(
            header,
            text="✕",
            font=('Helvetica', 14, 'bold'),
            bg=COLORS['secondary'],
            fg='white',
            cursor="hand2"
        )
        close_btn.pack(side=tk.RIGHT, padx=15, pady=10)
        close_btn.bind("<Button-1>", lambda e: self.hide_panels())

        # Content
        content = tk.Frame(self.settings_frame, bg=COLORS['background'], padx=15, pady=15)
        content.pack(fill=tk.BOTH, expand=True)

        # Action
        tk.Label(content, text="🎯 Action:", font=('Helvetica', 11),
                bg=COLORS['background'], fg=COLORS['text']).grid(row=0, column=0, sticky='w', pady=8)
        self.action_var = tk.StringVar(value="summarize")
        ttk.Combobox(content, textvariable=self.action_var,
                    values=["summarize", "paraphrase", "code_summarize"],
                    state="readonly", width=15).grid(row=0, column=1, pady=8, padx=10)

        # Style
        tk.Label(content, text="🎨 Style:", font=('Helvetica', 11),
                bg=COLORS['background'], fg=COLORS['text']).grid(row=1, column=0, sticky='w', pady=8)
        self.style_var = tk.StringVar(value="default")
        ttk.Combobox(content, textvariable=self.style_var,
                    values=["default", "academic", "casual", "business", "creative"],
                    state="readonly", width=15).grid(row=1, column=1, pady=8, padx=10)

        # Min words
        tk.Label(content, text="📏 Min Words:", font=('Helvetica', 11),
                bg=COLORS['background'], fg=COLORS['text']).grid(row=2, column=0, sticky='w', pady=8)
        self.min_length_var = tk.StringVar(value="100")
        ttk.Entry(content, textvariable=self.min_length_var, width=17).grid(row=2, column=1, pady=8, padx=10)

        # Max words
        tk.Label(content, text="📐 Max Words:", font=('Helvetica', 11),
                bg=COLORS['background'], fg=COLORS['text']).grid(row=3, column=0, sticky='w', pady=8)
        self.max_length_var = tk.StringVar(value="150")
        ttk.Entry(content, textvariable=self.max_length_var, width=17).grid(row=3, column=1, pady=8, padx=10)

        # Apply button
        btn_frame = tk.Frame(self.settings_frame, bg=COLORS['background'])
        btn_frame.pack(fill=tk.X, pady=15)

        tk.Button(
            btn_frame,
            text="✓ Apply",
            font=('Helvetica', 11, 'bold'),
            bg=COLORS['primary'],
            fg='white',
            relief='flat',
            padx=20,
            pady=8,
            cursor="hand2",
            command=self.apply_settings
        ).pack()

    def create_menu(self):
        """Create context menu."""
        self.menu = tk.Menu(self, tearoff=0, font=('Helvetica', 11))
        self.menu.add_command(label="  ✨ Summarize", command=lambda: self.process_action("summarize"))
        self.menu.add_command(label="  🔁 Paraphrase", command=lambda: self.process_action("paraphrase"))
        self.menu.add_command(label="  💻 Code Summarize", command=lambda: self.process_action("code_summarize"))
        self.menu.add_separator()
        self.menu.add_command(label="  ⚙️ Settings", command=self.show_settings)
        self.menu.add_command(label="  🎯 Hide", command=self.hide_panels)
        self.menu.add_separator()
        self.menu.add_command(label="  ❌ Quit", command=self.quit)

    def show_menu(self, event):
        """Show context menu."""
        self.menu.post(event.x_root, event.y_root)

    def start_drag(self, event):
        """Start drag."""
        self.offset_x = event.x
        self.offset_y = event.y

    def drag(self, event):
        """Drag window."""
        x = self.winfo_pointerx() - self.offset_x
        y = self.winfo_pointery() - self.offset_y
        self.geometry(f"+{x}+{y}")

    def process_action(self, action_type):
        """Process action."""
        self.action_type = action_type

        # On macOS, try to copy selected text
        if sys.platform == "darwin":
            try:
                subprocess.run([
                    "osascript", "-e",
                    'tell application "System Events" to keystroke "c" using {command down}'
                ], check=False, timeout=1)
            except:
                pass

        self.after(300, self.process_clipboard)

    def process_clipboard(self):
        """Process clipboard text."""
        try:
            text = pyperclip.paste()
        except Exception as e:
            self.show_result(f"Clipboard error: {e}", error=True)
            return

        if not text or not text.strip():
            self.show_result("No text in clipboard!\n\nCopy text first (Cmd+C), then try again.", error=True)
            return

        self.show_result("⏳ Processing...")
        self.update()

        try:
            if self.action_type == "summarize":
                result = summarize_text(text, self.max_length, self.min_length, self.writing_style)
                self.show_result(result, title="✨ Summary")
            elif self.action_type == "paraphrase":
                result = paraphrase_text(text, self.max_length, self.min_length, self.writing_style)
                self.show_result(result, title="🔁 Paraphrase")
            else:
                result = summarize_code(text, self.max_length, self.language)
                self.show_result(result, title="💻 Code Summary")
        except Exception as e:
            self.show_result(f"Error: {e}", error=True)

    def show_result(self, text, title="✨ Result", error=False):
        """Show result panel."""
        self.settings_frame.pack_forget()
        if self.pen_label:
            self.pen_label.pack_forget()

        color = COLORS['error'] if error else COLORS['primary']
        self.result_title.config(text=title, bg=color)
        self.result_title.master.config(bg=color)

        for w in self.result_title.master.winfo_children():
            w.config(bg=color)

        self.result_frame.pack(fill=tk.BOTH, expand=True)
        self.geometry("380x350")
        self.configure(bg=COLORS['background'])
        self.main_frame.configure(bg=COLORS['background'])

        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, text)

    def show_settings(self):
        """Show settings panel."""
        self.result_frame.pack_forget()
        if self.pen_label:
            self.pen_label.pack_forget()

        self.settings_frame.pack(fill=tk.BOTH, expand=True)
        self.geometry("300x310")
        self.configure(bg=COLORS['background'])
        self.main_frame.configure(bg=COLORS['background'])

    def apply_settings(self):
        """Apply settings."""
        try:
            self.action_type = self.action_var.get()
            self.writing_style = self.style_var.get()
            self.min_length = int(self.min_length_var.get())
            self.max_length = int(self.max_length_var.get())
        except ValueError:
            pass
        self.hide_panels()

    def copy_result(self):
        """Copy result to clipboard."""
        text = self.text_area.get(1.0, tk.END).strip()
        if text:
            pyperclip.copy(text)

    def hide_panels(self):
        """Hide panels and show pen."""
        self.result_frame.pack_forget()
        self.settings_frame.pack_forget()

        if self.pen_label:
            self.pen_label.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        self.geometry("90x90")
        self.configure(bg='#f0f0f0')
        self.main_frame.configure(bg='#f0f0f0')


if __name__ == "__main__":
    app = FloatingPen()
    app.mainloop()
