import tkinter as tk
from tkinter import ttk
import pyperclip
import sys
import subprocess
from summarizer import summarize_text, paraphrase_text, summarize_code


class Shortify(tk.Tk):
    def __init__(self):
        super().__init__()

        # App settings
        self.current_action = "summarize"
        self.current_style = "default"
        self.min_words = 100
        self.max_words = 150

        # Window setup
        self.title("Shortify")
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(bg="#667eea")

        # Drag variables
        self._drag_x = 0
        self._drag_y = 0

        # Current view
        self.current_view = "icon"

        # Build UI
        self.build_icon_view()
        self.build_result_view()
        self.build_settings_view()
        self.build_menu()

        # Show icon view
        self.show_icon()

    def build_icon_view(self):
        """Build the floating icon."""
        self.icon_frame = tk.Frame(self, bg="#667eea")

        # Pencil emoji as the icon
        self.icon_label = tk.Label(
            self.icon_frame,
            text="✏️",
            font=("Segoe UI Emoji", 32),
            bg="#667eea",
            fg="white",
            cursor="hand2"
        )
        self.icon_label.pack(padx=15, pady=15)

        # Bindings
        self.icon_label.bind("<Button-1>", self.start_drag)
        self.icon_label.bind("<B1-Motion>", self.do_drag)
        self.icon_label.bind("<Button-2>", self.show_context_menu)
        self.icon_label.bind("<Button-3>", self.show_context_menu)
        self.icon_label.bind("<Control-Button-1>", self.show_context_menu)

    def build_result_view(self):
        """Build the result display."""
        self.result_frame = tk.Frame(self, bg="#ffffff")

        # Header
        header = tk.Frame(self.result_frame, bg="#667eea")
        header.pack(fill=tk.X)

        self.result_icon = tk.Label(
            header, text="✨", font=("Segoe UI Emoji", 16),
            bg="#667eea", fg="white"
        )
        self.result_icon.pack(side=tk.LEFT, padx=(15, 5), pady=12)

        self.result_title = tk.Label(
            header, text="Summary", font=("Helvetica", 14, "bold"),
            bg="#667eea", fg="white"
        )
        self.result_title.pack(side=tk.LEFT, pady=12)

        close_btn = tk.Label(
            header, text="×", font=("Helvetica", 20, "bold"),
            bg="#667eea", fg="white", cursor="hand2"
        )
        close_btn.pack(side=tk.RIGHT, padx=15, pady=8)
        close_btn.bind("<Button-1>", lambda e: self.show_icon())

        # Make header draggable
        for widget in [header, self.result_icon, self.result_title]:
            widget.bind("<Button-1>", self.start_drag)
            widget.bind("<B1-Motion>", self.do_drag)

        # Content area
        content = tk.Frame(self.result_frame, bg="#ffffff", padx=15, pady=15)
        content.pack(fill=tk.BOTH, expand=True)

        # Text area with border
        text_border = tk.Frame(content, bg="#e0e0e0", padx=1, pady=1)
        text_border.pack(fill=tk.BOTH, expand=True)

        self.result_text = tk.Text(
            text_border,
            font=("Helvetica", 11),
            bg="#fafafa",
            fg="#333333",
            wrap=tk.WORD,
            padx=12,
            pady=12,
            relief="flat",
            highlightthickness=0
        )
        self.result_text.pack(fill=tk.BOTH, expand=True)

        # Bottom buttons
        btn_frame = tk.Frame(self.result_frame, bg="#ffffff", pady=12)
        btn_frame.pack(fill=tk.X)

        copy_btn = tk.Button(
            btn_frame,
            text="📋 Copy",
            font=("Helvetica", 10, "bold"),
            bg="#667eea",
            fg="white",
            activebackground="#5a6fd6",
            activeforeground="white",
            relief="flat",
            padx=20,
            pady=8,
            cursor="hand2",
            command=self.copy_to_clipboard
        )
        copy_btn.pack(side=tk.LEFT, padx=15)

        new_btn = tk.Button(
            btn_frame,
            text="🔄 New",
            font=("Helvetica", 10),
            bg="#f0f0f0",
            fg="#333333",
            activebackground="#e0e0e0",
            relief="flat",
            padx=20,
            pady=8,
            cursor="hand2",
            command=self.show_icon
        )
        new_btn.pack(side=tk.RIGHT, padx=15)

    def build_settings_view(self):
        """Build the settings panel."""
        self.settings_frame = tk.Frame(self, bg="#ffffff")

        # Header
        header = tk.Frame(self.settings_frame, bg="#764ba2")
        header.pack(fill=tk.X)

        tk.Label(
            header, text="⚙️", font=("Segoe UI Emoji", 16),
            bg="#764ba2", fg="white"
        ).pack(side=tk.LEFT, padx=(15, 5), pady=12)

        tk.Label(
            header, text="Settings", font=("Helvetica", 14, "bold"),
            bg="#764ba2", fg="white"
        ).pack(side=tk.LEFT, pady=12)

        close_btn = tk.Label(
            header, text="×", font=("Helvetica", 20, "bold"),
            bg="#764ba2", fg="white", cursor="hand2"
        )
        close_btn.pack(side=tk.RIGHT, padx=15, pady=8)
        close_btn.bind("<Button-1>", lambda e: self.show_icon())

        # Make header draggable
        for widget in header.winfo_children():
            widget.bind("<Button-1>", self.start_drag)
            widget.bind("<B1-Motion>", self.do_drag)
        header.bind("<Button-1>", self.start_drag)
        header.bind("<B1-Motion>", self.do_drag)

        # Content
        content = tk.Frame(self.settings_frame, bg="#ffffff", padx=20, pady=20)
        content.pack(fill=tk.BOTH, expand=True)

        # Style configurations
        label_font = ("Helvetica", 11)
        label_color = "#444444"

        # Row 0: Action
        tk.Label(
            content, text="🎯 Action", font=label_font,
            bg="#ffffff", fg=label_color, anchor="w"
        ).grid(row=0, column=0, sticky="w", pady=(0, 5))

        self.action_var = tk.StringVar(value=self.current_action)
        action_combo = ttk.Combobox(
            content,
            textvariable=self.action_var,
            values=["summarize", "paraphrase", "code_summarize"],
            state="readonly",
            width=20,
            font=("Helvetica", 10)
        )
        action_combo.grid(row=1, column=0, sticky="ew", pady=(0, 15))

        # Row 2: Style
        tk.Label(
            content, text="🎨 Writing Style", font=label_font,
            bg="#ffffff", fg=label_color, anchor="w"
        ).grid(row=2, column=0, sticky="w", pady=(0, 5))

        self.style_var = tk.StringVar(value=self.current_style)
        style_combo = ttk.Combobox(
            content,
            textvariable=self.style_var,
            values=["default", "academic", "casual", "business", "creative"],
            state="readonly",
            width=20,
            font=("Helvetica", 10)
        )
        style_combo.grid(row=3, column=0, sticky="ew", pady=(0, 15))

        # Row 4: Min Words
        tk.Label(
            content, text="📏 Minimum Words", font=label_font,
            bg="#ffffff", fg=label_color, anchor="w"
        ).grid(row=4, column=0, sticky="w", pady=(0, 5))

        self.min_var = tk.StringVar(value=str(self.min_words))
        min_entry = tk.Entry(
            content,
            textvariable=self.min_var,
            font=("Helvetica", 10),
            relief="solid",
            bd=1,
            highlightthickness=0
        )
        min_entry.grid(row=5, column=0, sticky="ew", pady=(0, 15), ipady=5)

        # Row 6: Max Words
        tk.Label(
            content, text="📐 Maximum Words", font=label_font,
            bg="#ffffff", fg=label_color, anchor="w"
        ).grid(row=6, column=0, sticky="w", pady=(0, 5))

        self.max_var = tk.StringVar(value=str(self.max_words))
        max_entry = tk.Entry(
            content,
            textvariable=self.max_var,
            font=("Helvetica", 10),
            relief="solid",
            bd=1,
            highlightthickness=0
        )
        max_entry.grid(row=7, column=0, sticky="ew", pady=(0, 20), ipady=5)

        content.columnconfigure(0, weight=1)

        # Save button
        btn_frame = tk.Frame(self.settings_frame, bg="#ffffff", pady=15)
        btn_frame.pack(fill=tk.X)

        save_btn = tk.Button(
            btn_frame,
            text="💾 Save Settings",
            font=("Helvetica", 11, "bold"),
            bg="#764ba2",
            fg="white",
            activebackground="#6a4190",
            activeforeground="white",
            relief="flat",
            padx=25,
            pady=10,
            cursor="hand2",
            command=self.save_settings
        )
        save_btn.pack()

    def build_menu(self):
        """Build context menu."""
        self.menu = tk.Menu(self, tearoff=0, font=("Helvetica", 11))

        self.menu.add_command(
            label="  ✨  Summarize",
            command=lambda: self.do_action("summarize")
        )
        self.menu.add_command(
            label="  🔁  Paraphrase",
            command=lambda: self.do_action("paraphrase")
        )
        self.menu.add_command(
            label="  💻  Explain Code",
            command=lambda: self.do_action("code_summarize")
        )
        self.menu.add_separator()
        self.menu.add_command(
            label="  ⚙️  Settings",
            command=self.show_settings
        )
        self.menu.add_separator()
        self.menu.add_command(
            label="  ❌  Quit",
            command=self.quit
        )

    def show_context_menu(self, event):
        """Display context menu."""
        self.menu.post(event.x_root, event.y_root)

    def start_drag(self, event):
        """Begin window drag."""
        self._drag_x = event.x
        self._drag_y = event.y

    def do_drag(self, event):
        """Handle window dragging."""
        x = self.winfo_pointerx() - self._drag_x
        y = self.winfo_pointery() - self._drag_y
        self.geometry(f"+{x}+{y}")

    def show_icon(self):
        """Show the icon view."""
        self.result_frame.pack_forget()
        self.settings_frame.pack_forget()
        self.icon_frame.pack()
        self.geometry("80x80")
        self.configure(bg="#667eea")
        self.current_view = "icon"

    def show_result(self, text, title="Summary", icon="✨", error=False):
        """Show the result view."""
        self.icon_frame.pack_forget()
        self.settings_frame.pack_forget()

        # Update header
        color = "#e74c3c" if error else "#667eea"
        self.result_icon.config(text=icon, bg=color)
        self.result_title.config(text=title, bg=color)
        self.result_icon.master.config(bg=color)

        # Update all header children
        for widget in self.result_icon.master.winfo_children():
            widget.config(bg=color)

        self.result_frame.pack(fill=tk.BOTH, expand=True)
        self.geometry("400x380")
        self.configure(bg="#ffffff")

        # Set text
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, text)

        self.current_view = "result"

    def show_settings(self):
        """Show settings view."""
        self.icon_frame.pack_forget()
        self.result_frame.pack_forget()

        # Sync variables with current settings
        self.action_var.set(self.current_action)
        self.style_var.set(self.current_style)
        self.min_var.set(str(self.min_words))
        self.max_var.set(str(self.max_words))

        self.settings_frame.pack(fill=tk.BOTH, expand=True)
        self.geometry("280x420")
        self.configure(bg="#ffffff")
        self.current_view = "settings"

    def save_settings(self):
        """Save settings and return to icon."""
        # Get values from form
        self.current_action = self.action_var.get()
        self.current_style = self.style_var.get()

        try:
            self.min_words = int(self.min_var.get())
            if self.min_words < 10:
                self.min_words = 10
        except ValueError:
            self.min_words = 100

        try:
            self.max_words = int(self.max_var.get())
            if self.max_words < self.min_words:
                self.max_words = self.min_words + 50
        except ValueError:
            self.max_words = 150

        # Return to icon
        self.show_icon()

    def do_action(self, action):
        """Perform the selected action."""
        self.current_action = action

        # Try to copy on macOS
        if sys.platform == "darwin":
            try:
                subprocess.run([
                    "osascript", "-e",
                    'tell application "System Events" to keystroke "c" using {command down}'
                ], timeout=1, check=False)
            except:
                pass

        self.after(300, self.process_text)

    def process_text(self):
        """Process clipboard text."""
        # Get clipboard
        try:
            text = pyperclip.paste()
        except Exception as e:
            self.show_result(f"Clipboard error:\n{e}", "Error", "⚠️", error=True)
            return

        if not text or not text.strip():
            self.show_result(
                "No text found in clipboard!\n\n"
                "1. Select text in any app\n"
                "2. Copy it (Cmd+C)\n"
                "3. Right-click the pencil\n"
                "4. Choose an action",
                "No Text", "📋", error=True
            )
            return

        # Show processing
        self.show_result("Processing...", "Please Wait", "⏳")
        self.update()

        # Process
        try:
            if self.current_action == "summarize":
                result = summarize_text(
                    text,
                    max_length=self.max_words,
                    min_length=self.min_words,
                    style=self.current_style
                )
                self.show_result(result, "Summary", "✨")

            elif self.current_action == "paraphrase":
                result = paraphrase_text(
                    text,
                    max_length=self.max_words,
                    min_length=self.min_words,
                    style=self.current_style
                )
                self.show_result(result, "Paraphrase", "🔁")

            else:  # code_summarize
                result = summarize_code(
                    text,
                    max_length=self.max_words
                )
                self.show_result(result, "Code Explanation", "💻")

        except Exception as e:
            self.show_result(f"Error:\n{e}", "Error", "⚠️", error=True)

    def copy_to_clipboard(self):
        """Copy result to clipboard."""
        text = self.result_text.get(1.0, tk.END).strip()
        if text:
            pyperclip.copy(text)


if __name__ == "__main__":
    app = Shortify()
    app.mainloop()
