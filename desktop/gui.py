import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import keyboard
import pyperclip
import math
from utils import resource_path
from summarizer import summarize_text, paraphrase_text, summarize_code

class FloatingPen(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Shortify")
        self.geometry("400x300")
        self.overrideredirect(True)
        self.attributes("-topmost", True)

        # Animation-related attributes
        self.hover_scale = 1.0
        self.opacity = 1.0
        self.fade_direction = -1

        # Settings
        self.action_type = "summarize"  # Default action
        self.min_length = 100
        self.max_length = 150
        self.writing_style = "default"
        self.language = None  # Initialize language attribute

        self.style = ttk.Style()
        self.style.configure("Custom.TFrame", background='white')

        self.main_frame = ttk.Frame(self, style="Custom.TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.setup_pen_icon()
        self.create_text_area()
        self.create_settings_panel()
        self.create_menu()

        self.configure(bg='white')
        self.attributes('-alpha', 1.0)
        self.attributes('-transparentcolor', 'white')

    def setup_pen_icon(self):
        image_path = resource_path("assets/pen.png")
        self.pen_image = Image.open(image_path).convert("RGBA")
        self.original_pen_image = self.pen_image.copy()
        self.pen_image = self.pen_image.resize((100, 100), Image.Resampling.LANCZOS)
        self.pen_photo = ImageTk.PhotoImage(self.pen_image)

        self.pen_label = tk.Label(self.main_frame, image=self.pen_photo, bg='white')
        self.pen_label.pack(fill=tk.BOTH, expand=True)
        self.pen_label.bind('<Enter>', self.on_hover_enter)
        self.pen_label.bind('<Leave>', self.on_hover_leave)
        self.pen_label.bind("<Button-3>", self.on_right_click)
        self.pen_label.bind("<Button-1>", self.start_drag)
        self.pen_label.bind("<B1-Motion>", self.drag)

    def create_text_area(self):
        self.text_area = tk.Text(
            self.main_frame,
            height=15,
            width=50,
            wrap=tk.WORD,
            font=('Helvetica', 12),
            bg='#f5f5f5',
            fg='#333333',
            padx=10,
            pady=10,
            relief="flat",
            borderwidth=1,  # Add a thin border for visibility
            insertbackground='#333333'  # Add a cursor color
        )
        # Add a vertical scrollbar to the text area
        text_scroll = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.text_area.yview)
        self.text_area.configure(yscrollcommand=text_scroll.set)
        
        # The scrollbar and text area will be packed together when needed
        self.text_scroll = text_scroll
        self.text_area.pack_forget()

    def create_settings_panel(self):
        # Create a frame that will contain settings
        self.settings_frame = ttk.Frame(self.main_frame)
        self.settings_frame.pack_forget()
        
        # Create a canvas with scrollbar for settings
        self.settings_canvas = tk.Canvas(self.settings_frame, borderwidth=0, highlightthickness=0, background='#f5f5f5')
        self.settings_scrollbar = ttk.Scrollbar(self.settings_frame, orient="vertical", command=self.settings_canvas.yview)
        self.settings_inner_frame = ttk.Frame(self.settings_canvas, style="Settings.TFrame")
        
        # Configure style for the inner frame
        self.style.configure("Settings.TFrame", background='#f5f5f5')
        
        # Configure the inner frame to expand to the canvas size
        self.settings_inner_frame.bind(
            "<Configure>",
            lambda e: self.settings_canvas.configure(scrollregion=self.settings_canvas.bbox("all"))
        )
        
        # Mouse wheel binding for scrolling
        def _on_mousewheel(event):
            self.settings_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        self.settings_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Create window inside canvas
        self.settings_canvas.create_window((0, 0), window=self.settings_inner_frame, anchor="nw")
        self.settings_canvas.configure(yscrollcommand=self.settings_scrollbar.set)
        
        # Set minimum size for canvas
        self.settings_canvas.config(width=300, height=250)
        
        # Configure styles for dropdown and entry fields
        self.style.configure("TCombobox", fieldbackground='white', background='white')
        self.style.map('TCombobox', fieldbackground=[('readonly', 'white')])
        self.style.configure("TEntry", fieldbackground='white', background='white')
        
        # Action Type Selection
        ttk.Label(self.settings_inner_frame, text="Action:", background='#f5f5f5', foreground='#333333').grid(row=0, column=0, sticky="w", pady=2, padx=5)
        self.action_var = tk.StringVar(value="summarize")
        action_options = ["summarize", "paraphrase", "code_summarize"]
        
        self.action_combobox = ttk.Combobox(
            self.settings_inner_frame, 
            textvariable=self.action_var,
            values=action_options,
            state="readonly",
            width=15,
            style="TCombobox"
        )
        self.action_combobox.grid(row=0, column=1, sticky="ew", pady=2, padx=5)
        
        # Code Language Selection (only visible for code summarization)
        ttk.Label(self.settings_inner_frame, text="Language:", background='#f5f5f5', foreground='#333333').grid(row=1, column=0, sticky="w", pady=2, padx=5)
        self.language_var = tk.StringVar(value="auto-detect")
        language_options = ["auto-detect", "python", "javascript", "java", "c++", "c#", "go", "ruby", "php", "swift", "typescript", "rust", "kotlin", "sql"]
        
        self.language_combobox = ttk.Combobox(
            self.settings_inner_frame, 
            textvariable=self.language_var,
            values=language_options,
            state="readonly",
            width=15,
            style="TCombobox"
        )
        self.language_combobox.grid(row=1, column=1, sticky="ew", pady=2, padx=5)
        
        # Writing Style Selection
        ttk.Label(self.settings_inner_frame, text="Style:", background='#f5f5f5', foreground='#333333').grid(row=2, column=0, sticky="w", pady=2, padx=5)
        self.style_var = tk.StringVar(value="default")
        style_options = ["default", "academic", "casual", "business", "creative"]
        
        self.style_combobox = ttk.Combobox(
            self.settings_inner_frame, 
            textvariable=self.style_var,
            values=style_options,
            state="readonly",
            width=15,
            style="TCombobox"
        )
        self.style_combobox.grid(row=2, column=1, sticky="ew", pady=2, padx=5)
        
        # Bind action change to update UI
        self.action_combobox.bind("<<ComboboxSelected>>", self.on_action_change)
        
        # Length Controls
        ttk.Label(self.settings_inner_frame, text="Min Length:", background='#f5f5f5', foreground='#333333').grid(row=3, column=0, sticky="w", pady=2, padx=5)
        self.min_length_var = tk.StringVar(value="100")
        self.min_length_entry = ttk.Entry(
            self.settings_inner_frame, 
            textvariable=self.min_length_var,
            width=7,
            style="TEntry"
        )
        self.min_length_entry.grid(row=3, column=1, sticky="w", pady=2, padx=5)
        
        ttk.Label(self.settings_inner_frame, text="Max Length:", background='#f5f5f5', foreground='#333333').grid(row=4, column=0, sticky="w", pady=2, padx=5)
        self.max_length_var = tk.StringVar(value="150")
        self.max_length_entry = ttk.Entry(
            self.settings_inner_frame, 
            textvariable=self.max_length_var,
            width=7,
            style="TEntry"
        )
        self.max_length_entry.grid(row=4, column=1, sticky="w", pady=2, padx=5)
        
        # Theme Selection
        ttk.Label(self.settings_inner_frame, text="Theme:", background='#f5f5f5', foreground='#333333').grid(row=5, column=0, sticky="w", pady=2, padx=5)
        self.theme_var = tk.StringVar(value="light")
        theme_options = ["light", "dark"]
        
        self.theme_combobox = ttk.Combobox(
            self.settings_inner_frame, 
            textvariable=self.theme_var,
            values=theme_options,
            state="readonly",
            width=15,
            style="TCombobox"
        )
        self.theme_combobox.grid(row=5, column=1, sticky="ew", pady=2, padx=5)
        self.theme_combobox.bind("<<ComboboxSelected>>", self.on_theme_change)
        
        # Apply Button
        self.apply_button = ttk.Button(
            self.settings_inner_frame,
            text="Apply",
            command=self.apply_settings
        )
        self.apply_button.grid(row=6, column=0, columnspan=2, pady=10, padx=5)
        
        # Add some extra space at the bottom to ensure all content is visible
        ttk.Label(self.settings_inner_frame, text="", background='#f5f5f5').grid(row=7, column=0, pady=10)
        
        # Pack canvas and scrollbar
        self.settings_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.settings_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Initial UI state setup
        self.on_action_change(None)

    def on_action_change(self, event):
        """Update UI based on selected action"""
        action = self.action_var.get()
        
        # Show/hide language selection for code summarization
        if action == "code_summarize":
            self.language_combobox.grid(row=1, column=1, sticky="ew", pady=2)
            self.style_combobox.grid_remove()
            self.min_length_entry.grid_remove()
        else:
            self.language_combobox.grid_remove()
            self.style_combobox.grid(row=2, column=1, sticky="ew", pady=2)
            self.min_length_entry.grid(row=3, column=1, sticky="w", pady=2)
            
    def on_theme_change(self, event):
        """Update UI colors based on selected theme"""
        theme = self.theme_var.get()
        
        # Update setting panel colors
        bg_color = '#1e1e1e' if theme == 'dark' else '#f5f5f5'
        fg_color = '#ffffff' if theme == 'dark' else '#333333'
        
        # Update canvas background
        self.settings_canvas.config(background=bg_color)
        
        # Update frame background
        self.style.configure("Settings.TFrame", background=bg_color)
        
        # Update labels
        for child in self.settings_inner_frame.winfo_children():
            if isinstance(child, ttk.Label):
                child.configure(background=bg_color, foreground=fg_color)
        
        # When in dark mode, ensure comboboxes and entries have white background
        # to make text readable
        if theme == "dark":
            self.style.configure("TCombobox", fieldbackground='white', foreground='black')
            self.style.map('TCombobox', fieldbackground=[('readonly', 'white')])
            self.style.configure("TEntry", fieldbackground='white', foreground='black')
        else:
            self.style.configure("TCombobox", fieldbackground='white', foreground='black')
            self.style.map('TCombobox', fieldbackground=[('readonly', 'white')])
            self.style.configure("TEntry", fieldbackground='white', foreground='black')
        
        # Update text area colors
        if theme == "dark":
            # Dark theme
            self.text_area.configure(
                bg='#1e1e1e',  # Dark background
                fg='#ffffff',  # White text
                insertbackground='#ffffff'  # White cursor
            )
            # Add a white border for visibility in dark mode
            self.text_area.configure(borderwidth=1, relief="solid")
        else:
            # Light theme
            self.text_area.configure(
                bg='#f5f5f5',  # Light background
                fg='#333333',  # Dark text
                insertbackground='#333333'  # Dark cursor
            )
            self.text_area.configure(borderwidth=1, relief="flat")

    def apply_settings(self):
        # Update settings based on user input
        try:
            self.action_type = self.action_var.get()
            
            if self.action_type == "code_summarize":
                self.max_length = int(self.max_length_var.get())
                self.language = self.language_var.get()
                if self.language == "auto-detect":
                    self.language = None
            else:
                self.min_length = int(self.min_length_var.get())
                self.max_length = int(self.max_length_var.get())
                self.writing_style = self.style_var.get()
                
                # Validate settings
                if self.min_length < 50:
                    self.min_length = 50
                    self.min_length_var.set("50")
                
                if self.max_length < self.min_length:
                    self.max_length = self.min_length + 50
                    self.max_length_var.set(str(self.max_length))
            
            # Apply theme change
            self.on_theme_change(None)
                
            # Hide settings panel
            self.settings_frame.pack_forget()
            self.geometry("100x100")  # Return to icon size
            
        except ValueError:
            self.show_error("Please enter valid numbers for length")

    def create_menu(self):
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.configure(font=('Helvetica', 10), bg='#ffffff', fg='#333333', relief="flat")
        self.menu.add_command(label="✨ Summarize", command=lambda: self.process_action("summarize"))
        self.menu.add_command(label="🔁 Paraphrase", command=lambda: self.process_action("paraphrase"))
        self.menu.add_command(label="💻 Code Summarize", command=lambda: self.process_action("code_summarize"))
        self.menu.add_command(label="⚙️ Settings", command=self.show_settings)
        self.menu.add_command(label="🎯 Hide", command=self.hide_text_area)
        self.menu.add_command(label="❌ Cancel", command=self.cancel_action)
        self.menu.add_command(label="🚫 Stop", command=self.stop_application)

    def show_settings(self):
        # Show settings panel
        self.text_area.pack_forget()
        self.text_scroll.pack_forget()
        
        # Update canvas background color based on theme
        theme = self.theme_var.get()
        bg_color = '#1e1e1e' if theme == 'dark' else '#f5f5f5'
        fg_color = '#ffffff' if theme == 'dark' else '#333333'
        
        # Update canvas and labels colors
        self.settings_canvas.config(background=bg_color)
        for child in self.settings_inner_frame.winfo_children():
            if isinstance(child, ttk.Label):
                child.configure(background=bg_color, foreground=fg_color)
        
        # Show settings with adjusted size
        self.settings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.geometry("350x350")  # Increased height for better visibility
        
        # Ensure the canvas is scrolled to the top
        self.settings_canvas.yview_moveto(0.0)
        
        # Update scrollbar now that content is visible
        self.settings_canvas.update_idletasks()
        self.settings_canvas.configure(scrollregion=self.settings_canvas.bbox("all"))

    def process_action(self, action_type):
        self.action_type = action_type
        keyboard.send('ctrl+c')
        self.after(200, self.process_clipboard_text)

    def process_clipboard_text(self):
        selected_text = pyperclip.paste()
        if selected_text.strip():
            if self.action_type == "summarize":
                result = summarize_text(
                    selected_text, 
                    max_length=self.max_length,
                    min_length=self.min_length,
                    style=self.writing_style
                )
                title = f"Summary ({self.writing_style} style)"
            elif self.action_type == "paraphrase":
                result = paraphrase_text(
                    selected_text, 
                    max_length=self.max_length,
                    min_length=self.min_length,
                    style=self.writing_style
                )
                title = f"Paraphrase ({self.writing_style} style)"
            else:  # code_summarize
                language_display = self.language if self.language else "auto-detected"
                result = summarize_code(
                    selected_text, 
                    max_length=self.max_length,
                    language=self.language
                )
                title = f"Code Summary ({language_display})"
            
            # Animate text area appearance
            self.geometry("450x350")  # Make the window a bit larger for scrollbar
            
            # Pack text area and scrollbar
            self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
            self.text_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
            
            self.text_area.delete(1.0, tk.END)
            
            # Add title
            self.text_area.insert(tk.END, f"{title}:\n\n", "title")
            self.text_area.tag_configure("title", font=("Helvetica", 12, "bold"))
            
            # Animate text insertion
            self.animate_text_insertion(result)
        else:
            self.show_error("No text selected!")

    def animate_text_insertion(self, text):
        """Animate text insertion character by character."""
        def insert_char(idx=0):
            if idx < len(text):
                self.text_area.insert(tk.END, text[idx])
                self.after(20, lambda: insert_char(idx + 1))
        
        insert_char()

    def show_message(self):
        # For backward compatibility
        self.process_action("summarize")

    def show_error(self, message):
        # Configure text area colors based on theme
        theme = getattr(self, 'theme_var', tk.StringVar(value="light")).get()
        
        if theme == "dark":
            bg_color = "#1e1e1e"
            fg_color = "#ffffff"
        else:
            bg_color = "#f5f5f5"
            fg_color = "#333333"
        
        self.geometry("400x300")
        self.text_area.configure(bg=bg_color, fg=fg_color)
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.text_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, f"Error: {message}", "error")
        self.text_area.tag_configure("error", foreground="#ff0000", font=("Helvetica", 12, "bold"))

    def on_right_click(self, event):
        self.menu.post(event.x_root, event.y_root)

    def start_drag(self, event):
        global offset_x, offset_y
        offset_x = event.x
        offset_y = event.y

    def drag(self, event):
        x = self.winfo_pointerx() - offset_x
        y = self.winfo_pointery() - offset_y
        self.geometry(f"+{x}+{y}")

    def cancel_action(self):
        self.menu.unpost()

    def hide_text_area(self):
        # Animate text area disappearance
        def fade_out(alpha=1.0):
            if alpha > 0:
                self.text_area.configure(bg=self.blend_colors('#f5f5f5', 'white', alpha))
                self.after(20, lambda: fade_out(alpha - 0.1))
            else:
                self.text_area.pack_forget()
                self.text_scroll.pack_forget()
                self.settings_frame.pack_forget()
                self.geometry("100x100")
        
        fade_out()

    def stop_application(self):
        # Animate application closure
        def fade_out(alpha=1.0):
            if alpha > 0:
                self.attributes('-alpha', alpha)
                self.after(20, lambda: fade_out(alpha - 0.1))
            else:
                self.destroy()
        
        fade_out()

    def blend_colors(self, color1, color2, ratio):
        """Helper method to blend two colors."""
        def parse_color(color):
            # Handle named colors and hex colors
            color_map = {
                'white': '#FFFFFF',
                'black': '#000000',
                'red': '#FF0000',
                # Add more named colors as needed
            }
            
            # Use the color map if it's a named color
            if color.lower() in color_map:
                color = color_map[color.lower()]
            
            # Remove hash if present
            color = color.lstrip('#')
            
            # Pad with zeros if needed
            color = color.zfill(6)
            
            return tuple(int(color[i:i+2], 16) for i in (0, 2, 4))

        r1, g1, b1 = parse_color(color1)
        r2, g2, b2 = parse_color(color2)
        
        r = int(r1 * ratio + r2 * (1 - ratio))
        g = int(g1 * ratio + g2 * (1 - ratio))
        b = int(b1 * ratio + b2 * (1 - ratio))
        
        return f'#{r:02x}{g:02x}{b:02x}'

    def on_hover_enter(self, event):
        """Handle hover enter event with scaling animation."""
        self.hover_scale = 1.1
        self.fade_direction = 1

    def on_hover_leave(self, event):
        """Handle hover leave event with scaling animation."""
        self.hover_scale = 1.0
        self.fade_direction = -1