import pandas as pd
import numpy as np

def calcular_pendientes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula la pendiente de cada actividad para el CPM extremo.

    La pendiente se define como (Ce - Cn) / (Dn - De). Si una actividad no puede reducirse (Dn = De), se asigna pendiente infinita para evitar divisiones por cero. El resultado se añade como una nueva columna en el DataFrame.

    Parámetros
    ----------
    df : pandas.DataFrame
        Actividades con duraciones normal/extrema y costes normal/extremo.

    Devuelve
    --------
    pandas.DataFrame
        Mismo DataFrame con la columna 'Pendiente' añadida.
    """

    denominador = df["Dn"] - df["De"]

    pendientes = []
    for dn_de, ce, cn in zip(denominador, df["Ce"], df["Cn"]):
        if dn_de == 0:
            pendientes.append(np.inf)
        else:
            pendientes.append((ce - cn) / dn_de)

    df["Pendiente"] = pendientes
    return df
