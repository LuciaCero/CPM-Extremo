import pandas as pd
import networkx as nx
from cpm_extremo import shared
from cpm_extremo import grafo as G

def calcular_tabla_holguras(grafo: nx.DiGraph, df_early_last: pd.DataFrame) -> pd.DataFrame:
    """
    Genera la tabla de holguras de todas las actividades reales del grafo AOA.

    Combina la información del grafo (nodos y duraciones) con los valores Early/Last de cada nodo, calcula la holgura Hij de cada actividad y determina si es crítica. Devuelve un DataFrame completo con todos los campos necesarios para el análisis CPM.

    Parámetros
    ----------
    grafo : nx.DiGraph
        Grafo AOA con actividades reales y ficticias.
    df_early_last : pandas.DataFrame
        Tabla con los valores Early y Last de cada nodo.

    Devuelve
    --------
    pandas.DataFrame
        Tabla con actividades, nodos, duraciones, holguras y criticidad.
    """

    # Obtener datos del grafo
    df_actividades = G.obtener_info_actividades(grafo)

    # Unir los df
    df_holguras = _unir_datos(df_early_last,df_actividades)

    # Calcular holgura y si es critica cada actividad
    df_holguras = _calcular_holguras(df_holguras)

    return df_holguras

def _unir_datos(df_early_last: pd.DataFrame, df_actividades: pd.DataFrame) -> pd.DataFrame:
    """
    Combina la información de actividades con los valores Early/Last de sus nodos.

    Realiza dos uniones:
    - Nodo_i -> añade Ei y Li
    - Nodo_j -> añade Ej y Lj

    Después elimina columnas intermedias no necesarias, dejando solo los valores relevantes para el cálculo de holguras.

    Parámetros
    ----------
    df_early_last : pandas.DataFrame
        Valores Early y Last de cada nodo.
    df_actividades : pandas.DataFrame
        Actividades reales con nodos inicial y final.

    Devuelve
    --------
    pandas.DataFrame
        Tabla de holguras con Ei y Lj.
    """

    # Merge para información del Nodo_i
    df_holguras = df_actividades.merge(
        df_early_last, left_on="Nodo_i", right_on="Nodo", how="left"
    ).rename(columns={"Early": "Ei", "Last": "Li"}).drop(columns="Nodo")
    
    # Merge para información del Nodo_j
    df_holguras = df_holguras.merge(
        df_early_last, left_on="Nodo_j", right_on="Nodo", how="left"
    ).rename(columns={"Early": "Ej", "Last": "Lj"}).drop(columns="Nodo")

    # Eliminamos columnas que no interesan (Li y Ej)
    df_holguras = df_holguras.drop(columns=["Li", "Ej"])

    return df_holguras

def _calcular_holguras(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula la holgura Hij de cada actividad y determina si es crítica.

    Aplica la fórmula estándar Hij = Lj - Ei - Dij y marca como crítica toda actividad con holgura cero. Además, registra la expresión simbólica y numérica utilizada para cada actividad.

    Parámetros
    ----------
    df : pandas.DataFrame
        Actividades con Ei, Lj y duración Dij.

    Devuelve
    --------
    pandas.DataFrame
        Tabla con holguras calculadas y columna booleana de criticidad.
    """

    shared.reset_holguras() # Limpiar antes de generar

    df["Hij"] = df["Lj"] - df["Ei"] - df["Dij"]
    df["Critica"] = df["Hij"] == 0

    for _, row in df.iterrows():
        act = row["Actividad"]
        i = row["Nodo_i"]
        j = row["Nodo_j"]
        Ei = row["Ei"]
        Lj = row["Lj"]
        Dij = row["Dij"]
        Hij = row["Hij"]

        shared.detalles_holguras.append(
            f"$H_{act} = H_{{{i},{j}}} = L_{j} - E_{i} - D_{{{act}}} = "
            f"{Lj} - {Ei} - {Dij} = {Hij}$"
        )

    return df