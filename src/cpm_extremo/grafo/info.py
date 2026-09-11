import networkx as nx
import pandas as pd

def obtener_info_nodos(grafo: nx.DiGraph) -> pd.DataFrame:
    """
    Extrae la información de todos los nodos del grafo AOA.

    Devuelve un DataFrame con los valores Early y Last almacenados en cada nodo,
    ordenado por identificador. Esta tabla se utiliza como base para cálculos
    posteriores de holguras y caminos críticos.

    Parámetros
    ----------
    grafo : nx.DiGraph
        Grafo AOA con los valores Early y Last ya calculados.

    Devuelve
    --------
    pandas.DataFrame
        Tabla con columnas: Nodo, Early, Last.
    """

    lista_nodos = []

    # Recorremos cada nodo, obteniendo su información
    for nodo, data in grafo.nodes(data=True):
        lista_nodos.append({
            "Nodo": nodo,
            "Early": data.get("early", 0),
            "Last": data.get("last", 0)
        })

    return pd.DataFrame(lista_nodos).sort_values("Nodo").reset_index(drop=True)

def obtener_info_actividades(grafo: nx.DiGraph, con_ficticias=False) -> pd.DataFrame:
    """
    Extrae la información de todas las actividades representadas en el grafo AOA.

    Recorre cada arista del grafo y construye un DataFrame con la actividad,
    nodos inicial y final, y duración. Por defecto ignora las actividades
    ficticias, aunque pueden incluirse si se necesita.

    Parámetros
    ----------
    grafo : nx.DiGraph
        Grafo AOA con actividades reales y ficticias.
    con_ficticias : bool, opcional
        Si es True, incluye también las actividades ficticias.

    Devuelve
    --------
    pandas.DataFrame
        Tabla con columnas: Actividad, Nodo_i, Nodo_j, Dij.
    """

    lista_actividades = []

    # Recorremos cada arista, obteniendo su información
    for u, v, data in grafo.edges(data=True):
        # Ignora actividades ficticias
        if (not con_ficticias) and (data.get("ficticia", False)):
            continue

        lista_actividades.append({
            "Actividad": data.get("actividad"),
            "Nodo_i": u,
            "Nodo_j": v,
            "Dij": data.get("duracion", 0)
        })

    return pd.DataFrame(lista_actividades).sort_values(by="Actividad").reset_index(drop=True)
