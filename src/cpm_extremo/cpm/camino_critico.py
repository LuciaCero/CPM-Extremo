import pandas as pd
import networkx as nx
from cpm_extremo import shared

def obtener_actividades_criticas_reducibles(df_actividades: pd.DataFrame, estado: pd.DataFrame, act_criticas: list) -> str | None:
    """
    Devuelve la actividad crítica reducible con menor pendiente.

    Evalúa cada actividad crítica y comprueba si aún puede reducirse
    (duración actual > duración extrema). Entre las candidatas, selecciona
    la que tenga la pendiente mínima. Si no existe ninguna reducible,
    devuelve None.

    Parámetros
    ----------
    df_actividades : pandas.DataFrame
        Tabla con información de las actividades.
    estado : pandas.DataFrame
        Estado actual de duraciones y coste del proyecto.
    act_criticas : list
        Lista de actividades críticas en la iteración actual.

    Devuelve
    --------
    str or None
        Actividad crítica reducible con menor pendiente, o None si no hay.
    """

    candidatas = []

    for act in act_criticas:

        # Si ya no es reducible        
        if act in shared.actividades_no_reducibles:
            continue

        duracion_actual = estado.loc[estado["Actividad"] == act, "Duracion"].values[0]
        duracion_extrema = df_actividades.loc[df_actividades["Actividad"] == act, "De"].values[0]

        # Si se puede reducir, es candidata 
        if duracion_actual > duracion_extrema:
            pendiente = df_actividades.loc[df_actividades["Actividad"] == act, "Pendiente"].values[0]

            candidatas.append((act, pendiente))

    if not candidatas:
        return None

    # Actividad con mínima pendiente (si hay empate, devuelve la primera)
    act_min = min(candidatas, key=lambda x: x[1])[0]

    return act_min

def obtener_actividades_criticas(df_holguras: pd.DataFrame) -> list:
    """
    Obtiene la lista de actividades críticas a partir de la tabla de holguras.

    Una actividad se considera crítica cuando su holgura total es cero (columna 'Critica' marcada como True).

    Parámetros
    ----------
    df_holguras : pandas.DataFrame
        Tabla de holguras.

    Devuelve
    --------
    list
        Actividades críticas de la iteración.
    """

    # Obtenemos las actividades críticas
    act_criticas = df_holguras.loc[df_holguras["Critica"] == True, "Actividad"].tolist() 

    return act_criticas

def calcular_caminos_criticos(grafo: nx.DiGraph, act_criticas: list) -> list:
    """
    Calcula todos los caminos críticos del proyecto a partir del grafo AOA.

    Construye un subgrafo formado únicamente por actividades críticas (y ficticias necesarias para conectar nodos críticos) y obtiene todos los caminos simples desde el nodo inicial al final. Cada camino se devuelve como una secuencia de actividades reales.

    Parámetros
    ----------
    grafo : nx.DiGraph
        Grafo AOA con actividades reales y ficticias.
    act_criticas : list
        Actividades críticas detectadas en la iteración actual.

    Devuelve
    --------
    list
        Lista de caminos críticos, cada uno como lista de actividades reales.
    """

    # Obtener nodos inicial y final
    nodos_inicio = [n for n in grafo.nodes if grafo.in_degree(n) == 0]
    nodo_inicio = nodos_inicio[0]
    nodos_fin = [n for n in grafo.nodes if grafo.out_degree(n) == 0]
    nodo_fin = nodos_fin[0]

    # Detectar nodos críticos (por actividades reales)
    nodos_criticos = set()
    for u, v, data in grafo.edges(data=True):
        if data.get("actividad") in act_criticas:
            nodos_criticos.add(u)
            nodos_criticos.add(v)

    # Crear subgrafo solo con actividades críticas
    grafo_critico = nx.DiGraph()

    # Añadir al subgrafo las tareas criticas
    for u, v, data in grafo.edges(data=True):
        es_real_critica = data.get("actividad") in act_criticas
        es_ficticia = data.get("duracion", 0) == 0

        if es_real_critica or (es_ficticia and u in nodos_criticos and v in nodos_criticos):
            grafo_critico.add_edge(u, v, **data)

    # Buscar todos los caminos posibles
    caminos_nodos = list(nx.all_simple_paths(grafo_critico, nodo_inicio, nodo_fin))

    # Pasamos los caminos de nodos a caminos de actividades
    caminos = []
    for camino in caminos_nodos:
        actividades_camino = []

        for i in range(len(camino) - 1):
            data = grafo[camino[i]][camino[i+1]]
            actividad = data.get("actividad")

            if actividad and not actividad.startswith("F_"):
                actividades_camino.append(actividad)
            
        if actividades_camino:
            caminos.append(actividades_camino)

    return caminos
