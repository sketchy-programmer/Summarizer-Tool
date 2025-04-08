import os
import sys
import tkinter as tk
from tkinter import simpledialog, messagebox
from dotenv import load_dotenv

# Try to load environment variables from multiple locations
# First try the current directory
load_dotenv()

# Also try the directory where the executable is located
if getattr(sys, 'frozen', False):
    exe_dir = os.path.dirname(sys.executable)
    env_path = os.path.join(exe_dir, '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)

# Get API key from environment
API_KEY = os.getenv('OPENAI_API_KEY')

# If no API key found, prompt the user
if not API_KEY:
    # Check if we're in a packaged app
    if getattr(sys, 'frozen', False):
        # Create a simple dialog to get the API key
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        # Show explanation message
        messagebox.showinfo(
            "API Key Required", 
            "Shortify needs an OpenAI API key to function.\n\n"
            "Please make sure the .env file is in the same directory as the executable.\n"
            "If you don't have the .env file, you can download it again from our website."
        )
        
        # Prompt for API key
        API_KEY = simpledialog.askstring(
            "OpenAI API Key Required", 
            "Please enter your OpenAI API key:",
            parent=root
        )
        
        # If user cancels or enters empty key
        if not API_KEY:
            messagebox.showerror(
                "No API Key", 
                "Shortify cannot function without an OpenAI API key. The application will now exit."
            )
            sys.exit(1)
        
        # Save key for future use
        try:
            with open(os.path.join(exe_dir, '.env'), 'w') as f:
                f.write(f'OPENAI_API_KEY={API_KEY}')
        except Exception:
            # If unable to save, just continue with the key in memory
            pass
    else:
        # Development environment - suggest creating .env file
        raise ValueError("Please set OPENAI_API_KEY in your .env file")