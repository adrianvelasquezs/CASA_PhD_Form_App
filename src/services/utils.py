# services.py
"""
Data manipulation utilities for CASA
author: Adrian Velasquez
"""

import os
import platform
from pathlib import Path

import pandas as pd


def load(filename: str, directory: str = './', extension: str = 'xlsx') -> pd.DataFrame:
    """
    Load data from a file
    :param filename: Name of the file
    :param directory: Directory where the file is located relative to the current directory
    :param extension: Extension of the file
    :return: Dataframe containing the data extracted from the file
    """
    file_path = os.path.join(directory, filename)
    normalized_extension = extension.lower().lstrip('.')
    if normalized_extension == 'xlsx':
        return pd.read_excel(file_path, index_col=0)
    if normalized_extension == 'csv':
        return pd.read_csv(filepath_or_buffer=file_path, index_col=0)
    raise ValueError(f'Unsupported extension: {extension}')


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform a dataframe to unify duplicated columns, transpose the criterio de aprendizaje,
    and encode the calificación
    :param df: Dataframe to transform
    :return: Dataframe with unified columns
    """
    df = unify(df)
    df = transpose(df)
    df = encode(df)
    final_df = df.drop(
        columns=[
            'ID',
            'Hora de inicio',
            'Hora de finalización',
            'Correo electrónico',
            'Nombre',
            'Hora de la última modificación'
        ],
        errors='ignore'
    )
    return final_df


def extract_cols(cols: list, prefixes: list) -> dict[str, list]:
    """
    Extract columns from a list
    :param cols: List of columns to extract
    :param prefixes: List of prefixes
    :return: Dictionary of prefixes and columns
    """
    extracted_cols = {}
    for prefix in prefixes:
        extracted_cols[prefix] = [col for col in cols if col.startswith(prefix)]
    return extracted_cols


def unify(df: pd.DataFrame) -> pd.DataFrame:
    """
    Unify a dataframe
    :param df: Dataframe to unify
    :return: Dataframe with unified columns
    """
    cols_to_extract = [
        'Estudiante',
        'Curso y sección'
    ]
    cols = df.columns.tolist()
    extracted = extract_cols(cols, cols_to_extract)
    estudiante_cols = extracted['Estudiante']
    curso_cols = extracted['Curso y sección']

    if not estudiante_cols or not curso_cols:
        raise ValueError('Could not find Estudiante or Curso y sección columns in the file.')

    # Unify columns
    df['Estudiante'] = df[estudiante_cols].bfill(axis=1).iloc[:, 0]
    df['Curso y sección'] = df[curso_cols].bfill(axis=1).iloc[:, 0]

    # Remove index 0 of estudiante_cols and curso_cols
    estudiante_cols = estudiante_cols[1:]
    curso_cols = curso_cols[1:]

    # Drop original Estudiante and Curso y sección columns
    df.drop(estudiante_cols + curso_cols, axis=1, inplace=True, errors='ignore')

    return df


def transpose(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transpose a dataframe
    :param df: Dataframe to transpose
    :return: Dataframe with transposed columns
    """
    cols = df.columns.tolist()
    criteria_cols = [col for col in cols if str(col) and str(col)[0].isdigit()]
    non_criteria = [col for col in cols if not (str(col) and str(col)[0].isdigit())]

    if not criteria_cols:
        raise ValueError('No criteria columns were found in the input file.')

    melted_df = df.melt(id_vars=non_criteria, value_vars=criteria_cols, var_name='Criterio de aprendizaje',
                        value_name='Calificación').dropna(subset=['Calificación'])
    return melted_df


def encode(df: pd.DataFrame) -> pd.DataFrame:
    """
    Encode a dataframe
    :param df: Dataframe to encode
    :return: Dataframe with encoded columns
    """
    values = {
        'Cumple plenamente': 5,
        'Cumple satisfactoriamente': 4,
        'Cumple deficientemente': 3,
        'No cumple': 2,
    }

    df['Calificación numérica'] = df['Calificación'].map(values)
    return df


def _get_windows_downloads_dir() -> Path | None:
    """Return Windows Downloads path using the Known Folder API."""
    if os.name != 'nt':
        return None

    try:
        import ctypes
        from ctypes import wintypes

        class GUID(ctypes.Structure):
            _fields_ = [
                ('Data1', wintypes.DWORD),
                ('Data2', wintypes.WORD),
                ('Data3', wintypes.WORD),
                ('Data4', ctypes.c_ubyte * 8),
            ]

        folder_id = GUID(
            0x374DE290,
            0x123F,
            0x4565,
            (ctypes.c_ubyte * 8)(0x91, 0x64, 0x39, 0xC4, 0x92, 0x5E, 0x46, 0x7B),
        )

        path_ptr = ctypes.c_wchar_p()
        shell32 = ctypes.windll.shell32
        get_known_folder_path = getattr(shell32, 'SHGetKnownFolderPath')
        result = get_known_folder_path(
            ctypes.byref(folder_id),
            0,
            None,
            ctypes.byref(path_ptr),
        )
        if result != 0:
            return None

        downloads_path = Path(path_ptr.value)
        ole32 = ctypes.windll.ole32
        free_memory = getattr(ole32, 'CoTaskMemFree')
        free_memory(path_ptr)
        return downloads_path
    except Exception:
        return None


def _resolve_xdg_download_dir() -> Path | None:
    """Resolve XDG download path from env/config for Linux-like systems."""
    xdg_env = os.getenv('XDG_DOWNLOAD_DIR')
    if xdg_env:
        return Path(xdg_env.replace('$HOME', str(Path.home()))).expanduser()

    config_path = Path.home() / '.config' / 'user-dirs.dirs'
    if not config_path.exists():
        return None

    try:
        for line in config_path.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('XDG_DOWNLOAD_DIR='):
                raw_value = line.split('=', maxsplit=1)[1].strip().strip('"')
                return Path(raw_value.replace('$HOME', str(Path.home()))).expanduser()
    except Exception:
        return None

    return None


def get_default_downloads_dir() -> str:
    """Get the best Downloads folder for the current OS and user settings."""
    system = platform.system().lower()

    if system == 'windows':
        windows_path = _get_windows_downloads_dir()
        if windows_path:
            return str(windows_path)
    elif system == 'linux':
        xdg_path = _resolve_xdg_download_dir()
        if xdg_path:
            return str(xdg_path)

    return str((Path.home() / 'Downloads').expanduser())


def save_df_as_excel(df: pd.DataFrame, output_dir: str | None = None, filename: str = 'casa_phd_output.xlsx') -> str:
    """
    Save dataframe to an Excel file in the selected directory.
    :param df: Dataframe to export
    :param output_dir: Destination folder. Uses Downloads when None.
    :param filename: Output filename
    :return: Full output path
    """
    target_dir = Path(output_dir or get_default_downloads_dir()).expanduser()
    target_dir.mkdir(parents=True, exist_ok=True)
    output_path = target_dir / filename
    df.to_excel(output_path, index=False)
    return str(output_path)


def download_df_as_excel(df: pd.DataFrame, dl_path: str | None = None) -> bool:
    """
    Download the dataframe into the downloads folder
    :param df: Dataframe to download
    :param dl_path: Path to the download folder
    :return: True if successful, False otherwise
    """
    try:
        save_df_as_excel(df=df, output_dir=dl_path)
    except Exception:
        return False
    return True
