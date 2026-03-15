# gui.py
"""
GUI definition for the application
Allows the user to upload an Excel file, transform it with the pre-defined procedures and download it.
"""

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

import pandas as pd

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
        self.geometry("500x500")
        self.minsize(500, 500)

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

        self.input_file_var = tk.StringVar(value='Ningún archivo seleccionado')
        self.output_dir_var = tk.StringVar(value=ut.get_default_downloads_dir())
        self.status_var = tk.StringVar(value='Selecciona un archivo para comenzar.')
        self.result_var = tk.StringVar(value='')

        self.processed_df: pd.DataFrame | None = None
        self.input_file_path: str | None = None

        # ===================
        # Build

        self._build_ui()

    # ===================
    # UI construction

    def _build_ui(self):
        self.main_frame = ttk.Frame(self, style='TFrame', padding=20)
        self.main_frame.pack(fill='both', expand=True)

        panel = ttk.Frame(self.main_frame, style='Panel.TFrame', padding=20)
        panel.pack(fill='both', expand=True)

        ttk.Label(panel, text='Transformador de datos CASA', style='Title.TLabel').pack(anchor='w')
        ttk.Label(
            panel,
            text='Sube un archivo, procesa la información y guarda el resultado en la carpeta que elijas.',
            style='Small.TLabel'
        ).pack(anchor='w', pady=(4, 18))

        upload_row = ttk.Frame(panel, style='Panel.TFrame')
        upload_row.pack(fill='x', pady=6)
        ttk.Label(upload_row, text='Archivo de entrada:', style='Section.TLabel').pack(side='left')
        ttk.Button(upload_row, text='Seleccionar archivo', style='Small.TButton', command=self._pick_input_file).pack(
            side='right'
        )
        ttk.Label(panel, textvariable=self.input_file_var, style='Result.TLabel').pack(fill='x', pady=(2, 12))

        output_row = ttk.Frame(panel, style='Panel.TFrame')
        output_row.pack(fill='x', pady=6)
        ttk.Label(output_row, text='Carpeta de salida:', style='Section.TLabel').pack(side='left')
        ttk.Button(output_row, text='Elegir carpeta', style='Small.TButton', command=self._pick_output_dir).pack(
            side='right'
        )
        ttk.Label(panel, textvariable=self.output_dir_var, style='Result.TLabel').pack(fill='x', pady=(2, 12))

        action_row = ttk.Frame(panel, style='Panel.TFrame')
        action_row.pack(fill='x', pady=(6, 10))

        self.process_button = ttk.Button(
            action_row,
            text='Procesar archivo',
            style='Accent.TButton',
            command=self._process_file,
        )
        self.process_button.pack(side='left')

        self.save_button = ttk.Button(
            action_row,
            text='Guardar resultado',
            style='Nav.TButton',
            command=self._save_result,
            state='disabled'
        )
        self.save_button.pack(side='left', padx=(10, 0))

        ttk.Label(panel, text='Resultado', style='Section.TLabel').pack(anchor='w', pady=(12, 4))
        ttk.Label(panel, textvariable=self.result_var, style='Result.TLabel', justify='left').pack(fill='x', pady=(0, 10))
        ttk.Label(panel, textvariable=self.status_var, style='Status.TLabel').pack(anchor='w')

    # ===================
    # UI helpers

    def _set_status(self, message: str):
        self.status_var.set(message)

    def _pick_input_file(self):
        selected_file = filedialog.askopenfilename(
            title='Seleccionar archivo de entrada',
            filetypes=[
                ('Excel files', '*.xlsx'),
                ('CSV files', '*.csv'),
                ('Supported files', '*.xlsx *.csv'),
            ],
        )
        if not selected_file:
            return

        self.input_file_path = selected_file
        self.input_file_var.set(selected_file)
        self.result_var.set('')
        self.processed_df = None
        self.save_button.configure(state='disabled')
        self._set_status('Archivo cargado. Presiona "Procesar archivo".')

    def _pick_output_dir(self):
        selected_folder = filedialog.askdirectory(
            title='Seleccionar carpeta de salida',
            initialdir=self.output_dir_var.get() or ut.get_default_downloads_dir(),
        )
        if selected_folder:
            self.output_dir_var.set(selected_folder)
            self._set_status('Carpeta de salida actualizada.')

    def _process_file(self):
        if not self.input_file_path:
            self._set_status('Primero selecciona un archivo de entrada.')
            return

        input_path = Path(self.input_file_path)
        extension = input_path.suffix.lower().lstrip('.')

        try:
            df = ut.load(filename=input_path.name, directory=str(input_path.parent), extension=extension)
            self.processed_df = ut.transform(df)
        except Exception as exc:
            self.processed_df = None
            self.save_button.configure(state='disabled')
            self.result_var.set('')
            self._set_status(f'Error al procesar el archivo: {exc}')
            return

        self.save_button.configure(state='normal')
        self.result_var.set(
            f'Filas procesadas: {len(self.processed_df)} | Columnas: {len(self.processed_df.columns)}'
        )
        self._set_status('Procesamiento completado. Ahora puedes guardar el archivo de salida.')

    def _save_result(self):
        if self.processed_df is None:
            self._set_status('No hay resultados para guardar. Procesa un archivo primero.')
            return

        output_dir = self.output_dir_var.get().strip() or ut.get_default_downloads_dir()
        try:
            output_path = ut.save_df_as_excel(df=self.processed_df, output_dir=output_dir)
        except Exception as exc:
            self._set_status(f'No se pudo guardar el archivo: {exc}')
            return

        self._set_status(f'Archivo guardado correctamente en: {output_path}')


# ====================================================================================================================
# Entrypoint

def run():
    app = PhdDataApp()
    app.mainloop()


if __name__ == '__main__':
    run()
