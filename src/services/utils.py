# services.py
"""
Data manipulation utilities for CASA
author: Adrian Velasquez
"""

import pandas as pd
import os


def load( filename: str, directory: str = './', extension:str = 'xlsx' ) -> pd.DataFrame:
    """
    Load data from a file
    :param filename: Name of the file
    :param directory: Directory where the file is located relative to the current directory
    :param extension: Extension of the file
    :return: Dataframe containing the data extracted from the file
    """
    df = pd.DataFrame()
    if extension == 'xlsx':
        df = pd.read_excel(os.path.join(directory, filename), index_col=0)
    elif extension == 'csv':
        df = pd.read_csv(os.path.join(directory, filename), index_col=0)
    return df


def transform( df: pd.DataFrame ) -> pd.DataFrame:
    """
    Transform a dataframe to unify duplicated columns, transpose the criterio de aprendizaje,
    and encode the calificación
    :param df: Dataframe to transform
    :return: Dataframe with unified columns
    """
    df = unify( df )
    df = transpose( df )
    df = encode( df )
    final_df = df.drop(columns=['ID', 'Hora de inicio', 'Hora de finalización', 'Correo electrónico', 'Nombre',
                                       'Hora de la última modificación'])
    return final_df


def extract_cols( cols: list, prefixes: list ) -> dict[str, list]:
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


def unify( df: pd.DataFrame ) -> pd.DataFrame:
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
    estudiante_cols, curso_cols = extract_cols(cols, cols_to_extract)

    # Unify columns
    df['Estudiante'] = df[estudiante_cols].bfill(axis=1).iloc[:, 0]
    df['Curso y sección'] = df[curso_cols].bfill(axis=1).iloc[:, 0]

    # Remove index 0 of estudiante_cols and curso_cols
    estudiante_cols = estudiante_cols[1:]
    curso_cols = curso_cols[1:]

    # Drop original Estudiante and Curso y sección columns
    df.drop(estudiante_cols + curso_cols, axis=1, inplace=True)

    return df


def transpose( df: pd.DataFrame ) -> pd.DataFrame:
    """
    Transpose a dataframe
    :param df: Dataframe to transpose
    :return: Dataframe with transposed columns
    """
    cols = df.columns.tolist()
    criteria_cols = [col for col in cols if col[0].isdigit()]
    non_criteria = [col for col in cols if not col[0].isdigit()]

    melted_df = df.melt(id_vars=non_criteria, value_vars=criteria_cols, var_name='Criterio de aprendizaje',
                        value_name='Calificación').dropna(subset=['Calificación'])
    return melted_df


def encode( df: pd.DataFrame ) -> pd.DataFrame:
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


def download_df_as_excel( df: pd.DataFrame, dl_path: str = '~/Descargas' ) -> bool:
    """
    Download the dataframe into the downloads folder
    :param df: Dataframe to download
    :param dl_path: Path to the download folder
    :return: True if successful, False otherwise
    """
    downloads_dir = os.path.expanduser(dl_path)
    try:
        os.makedirs(downloads_dir, exist_ok=True)
        output_path = os.path.join(downloads_dir, 'casa_output.xlsx')
        df.to_excel(output_path, index=False)
    except Exception as e:
        return False
    return True
