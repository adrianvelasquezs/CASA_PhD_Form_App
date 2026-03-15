# gui.py
"""
GUI definition for the application
Allows the user to upload an Excel file, transform it with the pre-defined procedures and download it.
"""

import tkinter as tk
from tkinter import ttk

import services.utils as ut

from public.styles import COLORS


# ====================================================================================================================
# Static


# ====================================================================================================================
# App

class PhdDataApp(tk.Tk):
    """
    PhdDataApp class
    Defines the main window for the application
    """

    def __init__(self):
        super().__init__()
        self.title("Transformación de datos PhD")
        self.configure(bg=COLORS['bg'])
        self.geometry("1440x860")
        self.minsize(1200, 700)

        # ===================
        # Styling

        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TFrame', background=COLORS['bg'])
        style.configure('Panel.TFrame', background=COLORS['panel'])
        style.configure('TLabel', background=COLORS['panel'], foreground=COLORS['text'],
                        font=('Segoe UI', 10))
        style.configure('Title.TLabel', background=COLORS['panel'], foreground=COLORS['text_bright'],
                        font=('Segoe UI', 13, 'bold'))
        style.configure('Section.TLabel', background=COLORS['panel'], foreground=COLORS['accent'],
                        font=('Segoe UI', 11, 'bold'))
        style.configure('Small.TLabel', background=COLORS['panel'], foreground=COLORS['text_dim'],
                        font=('Segoe UI', 9))
        style.configure('Status.TLabel', background=COLORS['bg'], foreground=COLORS['text_dim'],
                        font=('Segoe UI', 9))
        style.configure('Result.TLabel', background=COLORS['panel'], foreground=COLORS['text'],
                        font=('Consolas', 10))
        style.configure('Accent.TButton', background=COLORS['btn_primary'],
                        foreground='white', font=('Segoe UI', 11, 'bold'),
                        padding=(20, 10))
        style.map('Accent.TButton',
                  background=[('active', COLORS['btn_hover']),
                              ('pressed', COLORS['accent'])])
        style.configure('Small.TButton', background=COLORS['accent2'],
                        foreground=COLORS['text'], font=('Segoe UI', 9),
                        padding=(8, 4))
        style.map('Small.TButton',
                  background=[('active', COLORS['btn_secondary']),])
        style.configure('Nav.TButton', background=COLORS['panel_light'],
                        foreground=COLORS['text'], font=('Segoe UI', 10, 'bold'),
                        padding=(16, 8))
        style.map('Nav.TButton',
                  background=[('active', COLORS['accent2'])])

        # ===================
        # Build

        self._build_ui()

    # ===================
    # UI construction

    def _build_ui(self):
        self.main_frame = ttk.Frame(self, style='TFrame')
        self.main_frame.pack(fill='both', expand=True)

        # We have two screens: Editor & Results
        self.editor_frame = ttk.Frame(self.main_frame, style='TFrame')

        self.editor_frame.pack(fill='both', expand=True)

    # ===================
    # UI helpers


# ====================================================================================================================
# Entrypoint

def run():
    app = PhdDataApp()
    app.mainloop()


if __name__ == '__main__':
    run()
