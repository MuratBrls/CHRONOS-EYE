"""
CHRONOS-EYE Standalone Launcher
"""
from src.app import ChronosApp
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    # Add application icon if available
    # root.iconbitmap("path/to/icon.ico")
    app = ChronosApp(root)
    root.mainloop()
