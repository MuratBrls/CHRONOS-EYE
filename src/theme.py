"""
Modern Dark Theme for CHRONOS-EYE.
"""
import tkinter as tk
from tkinter import ttk

# Modern Color Palette - Deep Blue/Purple
BG_DARK = "#0A0E27"  # Deep navy
BG_PANEL = "#141B2D"  # Slightly lighter navy
TEXT_PRIMARY = "#E8EAF6"  # Soft white
TEXT_SECONDARY = "#9FA8C7"  # Muted blue-gray
ACCENT_PRIMARY = "#5B8FF9"  # Modern blue
ACCENT_SECONDARY = "#7C60FF"  # Modern purple
ACCENT_SUCCESS = "#00D9A8"  # Cyan green
ACCENT_WARNING = "#FFB74D"
ACCENT_ERROR = "#FF6B9D"
BORDER_COLOR = "#1E2A47"

class ChronosTheme:
    """Modern styling for CHRONOS-EYE GUI."""
    
    def __init__(self, root):
        self.root = root
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
    def apply(self):
        # Configure Root
        self.root.configure(bg=BG_DARK)
        
        # Frame
        self.style.configure("TFrame", background=BG_DARK)
        self.style.configure("Panel.TFrame", background=BG_PANEL, borderwidth=0, relief="flat")
        
        # Labels
        self.style.configure("TLabel", background=BG_DARK, foreground=TEXT_PRIMARY, font=("Segoe UI", 10))
        self.style.configure("Header.TLabel", background=BG_DARK, foreground=TEXT_PRIMARY, font=("Segoe UI", 20, "bold"))
        self.style.configure("PanelHeader.TLabel", background=BG_PANEL, foreground=ACCENT_PRIMARY, font=("Segoe UI", 12, "bold"))
        self.style.configure("Secondary.TLabel", background=BG_DARK, foreground=TEXT_SECONDARY, font=("Segoe UI", 9))
        self.style.configure("PanelSecondary.TLabel", background=BG_PANEL, foreground=TEXT_SECONDARY, font=("Segoe UI", 9))
        
        # Buttons - Modern gradient-like effect
        self.style.configure("TButton", 
                           padding=10, 
                           font=("Segoe UI", 10),
                           background=BG_PANEL,
                           foreground=TEXT_PRIMARY,
                           borderwidth=1,
                           relief="flat")
        self.style.configure("Accent.TButton", 
                           background=ACCENT_PRIMARY, 
                           foreground="white",
                           font=("Segoe UI", 10, "bold"),
                           borderwidth=0)
        self.style.map("Accent.TButton", 
                       background=[('active', ACCENT_SECONDARY), ('disabled', '#1E293B')],
                       foreground=[('disabled', '#475569')])
        
        # Input
        self.style.configure("TEntry", 
                           fieldbackground=BG_PANEL, 
                           foreground=TEXT_PRIMARY, 
                           borderwidth=1,
                           relief="flat")
        
        # Notebook / Tabs - Modern flat design
        self.style.configure("TNotebook", background=BG_DARK, borderwidth=0, tabmargins=[2, 5, 2, 0])
        self.style.configure("TNotebook.Tab", 
                           background=BG_DARK, 
                           foreground=TEXT_SECONDARY, 
                           padding=[24, 12], 
                           font=("Segoe UI", 10),
                           borderwidth=0)
        self.style.map("TNotebook.Tab", 
                       background=[('selected', BG_PANEL), ('active', '#1A2238')],
                       foreground=[('selected', ACCENT_PRIMARY), ('active', TEXT_PRIMARY)])
        
        # Labelframe
        self.style.configure("TLabelframe", 
                           background=BG_DARK, 
                           foreground=TEXT_PRIMARY, 
                           borderwidth=1, 
                           relief="flat",
                           bordercolor=BORDER_COLOR)
        self.style.configure("TLabelframe.Label", 
                           background=BG_DARK, 
                           foreground=ACCENT_PRIMARY, 
                           font=("Segoe UI", 11, "bold"))
        
        # Treeview - Sleek modern table
        self.style.configure("Treeview", 
                           background=BG_PANEL, 
                           fieldbackground=BG_PANEL, 
                           foreground=TEXT_PRIMARY,
                           borderwidth=0,
                           rowheight=90)
        self.style.configure("Treeview.Heading", 
                           background=BG_DARK, 
                           foreground=ACCENT_PRIMARY,
                           font=("Segoe UI", 10, "bold"),
                           borderwidth=0,
                           relief="flat")
        self.style.map("Treeview", 
                      background=[('selected', ACCENT_PRIMARY)],
                      foreground=[('selected', 'white')])
        
        # Combobox - Windows requires special handling
        self.style.configure("TCombobox",
                           fieldbackground=BG_PANEL,
                           background=BG_PANEL,
                           foreground=TEXT_PRIMARY,
                           arrowcolor=ACCENT_PRIMARY,
                           borderwidth=1,
                           relief="flat")
        self.style.map("TCombobox",
                      fieldbackground=[('readonly', BG_PANEL)],
                      selectbackground=[('readonly', BG_PANEL)],
                      selectforeground=[('readonly', TEXT_PRIMARY)])
        
        # Configure combobox dropdown colors (Windows)
        self.root.option_add('*TCombobox*Listbox*Background', BG_PANEL)
        self.root.option_add('*TCombobox*Listbox*Foreground', TEXT_PRIMARY)
        self.root.option_add('*TCombobox*Listbox*selectBackground', ACCENT_PRIMARY)
        self.root.option_add('*TCombobox*Listbox*selectForeground', 'white')
        
        # Progressbar - Modern gradient
        self.style.configure("TProgressbar",
                           background=ACCENT_PRIMARY,
                           troughcolor=BG_PANEL,
                           borderwidth=0,
                           thickness=6)


