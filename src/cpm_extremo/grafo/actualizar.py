import networkx as nx
import pandas as pd

def actualizar_duraciones(grafo: nx.DiGraph, estado: pd.DataFrame):
    """
    Actualiza las duraciones de las actividades reales del grafo AOA.

    Toma las duraciones actuales del estado del proyecto y las asigna a las aristas correspondientes del grafo, ignorando las actividades ficticias. Esto permite que el grafo refleje siempre las duraciones vigentes en cada iteración del CPM extremo.

    Parámetros
    ----------
    grafo : nx.DiGraph
        Grafo AOA con actividades reales y ficticias.
    estado : pandas.DataFrame
        Estado actual del proyecto con las duraciones vigentes de cada actividad.
    """


    # Sacamos del estado las duraciones junto con su actividad
    duraciones = dict(
        zip(estado["Actividad"], estado["Duracion"])
    )

    # Recorremos todas las aristas / actividades y modificamos las necesarias
    for _, _, data in grafo.edges(data=True):
        if not data.get("ficticia", False) :
            act = data["actividad"]

            if act in duraciones:
                data["duracion"] = duraciones[act]
