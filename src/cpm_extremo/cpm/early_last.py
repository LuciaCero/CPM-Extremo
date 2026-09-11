import pandas as pd
import networkx as nx
from cpm_extremo import grafo as G 
from cpm_extremo import shared

def calcular_early_last(grafo: nx.DiGraph) -> pd.DataFrame:
    """
    Calcula los valores Early y Last de todos los nodos del grafo AOA.

    Inicializa los campos, ejecuta el cálculo de Early y Last siguiendo el orden topológico, y devuelve una tabla con la información resultante de cada nodo.

    Parámetros
    ----------
    grafo : nx.DiGraph
        Grafo AOA con duraciones en sus aristas.

    Devuelve
    --------
    pandas.DataFrame
        Tabla con los valores Early y Last de cada nodo.
    """
    
    _inicializar_early_last(grafo)
    _calcular_early_grafo(grafo)
    _calcular_last_grafo(grafo)

    return G.obtener_info_nodos(grafo)

def _inicializar_early_last(grafo: nx.DiGraph):
    """
    Inicializa los valores Early y Last de todos los nodos del grafo.

    Establece ambos campos a None para preparar el cálculo posterior.
    
    Parámetros
    ----------
    grafo : nx.DiGraph
        Grafo AOA cuyos nodos serán inicializados.
    """

    for nodo in grafo.nodes():
        grafo.nodes[nodo]["early"] = None
        grafo.nodes[nodo]["last"] = None

def _calcular_early_grafo(grafo: nx.DiGraph):
    """
    Calcula los valores Early de todos los nodos del grafo.

    Recorre los nodos en orden topológico y asigna a cada uno el valor Early. Resetea la variable que almacena los detalles simbólicos del cálculo.

    Parámetros
    ----------
    grafo : nx.DiGraph
        Grafo AOA sobre el que se realiza el cálculo.
    """

    shared.reset_early() # Limpiar antes de generar

    # Recorremos todos los nodos y se calcula el early de cada uno
    for nodo in nx.topological_sort(grafo):
        grafo.nodes[nodo]["early"] = _calcular_early_nodo(grafo, nodo)

def _calcular_early_nodo(grafo: nx.DiGraph, nodo: int):
    """
    Calcula el valor Early de un nodo específico.

    Si el nodo no tiene predecesores, su Early es 0. En caso contrario, toma el máximo entre (Early del nodo predecesor + duración de la actividad). Registra la fórmula simbólica y numérica utilizada para añadirlos a la salida output_pert.txt.

    Parámetros
    ----------
    grafo : nx.DiGraph
        Grafo AOA con duraciones en las aristas.
    nodo : int
        Nodo cuyo valor Early se desea calcular.

    Devuelve
    --------
    int or float
        Valor Early del nodo.
    """

    if grafo.in_degree(nodo) == 0:
        shared.detalles_early.append(f"$E_{nodo} = 0$")
        return 0

    partes_formula = []
    partes_valores = []
    partes_sumas = []

    for u, _, data in grafo.in_edges(nodo, data=True):
        act = data.get("actividad", "")
        dur = data.get("duracion", 0)
        Ei = grafo.nodes[u]["early"]

        partes_formula.append(f"E_{u} + {act}")
        partes_valores.append(f"{Ei} + {dur}")
        partes_sumas.append(f"{Ei + dur}")

    resultado = max([grafo.nodes[u]["early"] + data.get("duracion", 0)
                     for u, _, data in grafo.in_edges(nodo, data=True)])

    shared.detalles_early.append(
        f"$E_{nodo} = Max \\{{{', '.join(partes_formula)}\\}} = "
        f"Max \\{{{', '.join(partes_valores)}\\}} = "
        f"Max \\{{{', '.join(partes_sumas)}\\}} = {resultado}$"
    )

    return resultado

def _calcular_last_grafo(grafo: nx.DiGraph):
    """
    Calcula los valores Last de todos los nodos del grafo.

    Inicializa el nodo final con su valor Early (duración total del proyecto) y recorre los nodos en orden topológico inverso. Resetea la variable que almacena los detalles simbólicos del cálculo.

    Parámetros
    ----------
    grafo : nx.DiGraph
        Grafo AOA sobre el que se realiza el cálculo.
    """

    shared.reset_last() # Limpiar antes de generar

    # Nodo final
    nodo_final = max(grafo.nodes())
    duracion_proyecto = grafo.nodes[nodo_final]["early"]

    # Last del nodo final
    grafo.nodes[nodo_final]["last"] = duracion_proyecto

    # Recorremos todos los nodos y se calcula el last de cada uno
    for nodo in reversed(list(nx.topological_sort(grafo))):
        grafo.nodes[nodo]["last"] = _calcular_last_nodo(grafo, nodo)

def _calcular_last_nodo(grafo: nx.DiGraph, nodo: int):
    """
    Calcula el valor Last de un nodo específico.

    Si el nodo no tiene sucesores, su Last coincide con su Early. En caso contrario, toma el mínimo entre (Last del sucesor - duración de la actividad). Registra la fórmula simbólica y numérica utilizada para añadirlos a la salida output_pert.txt.

    Parámetros
    ----------
    grafo : nx.DiGraph
        Grafo AOA con duraciones en las aristas.
    nodo : int
        Nodo cuyo valor Last se desea calcular.

    Devuelve
    --------
    int or float
        Valor Last del nodo.
    """

    if grafo.out_degree(nodo) == 0:
        val = grafo.nodes[nodo]["last"]
        shared.detalles_last.append(f"$L_{nodo} = E_{nodo} = {val}$")
        return val

    partes_formula = []
    partes_valores = []
    partes_restas = []

    for _, v, data in grafo.out_edges(nodo, data=True):
        act = data.get("actividad", "")
        dur = data.get("duracion", 0)
        Lv = grafo.nodes[v]["last"]

        partes_formula.append(f"L_{v} - {act}")
        partes_valores.append(f"{Lv} - {dur}")
        partes_restas.append(f"{Lv - dur}")

    resultado = min([grafo.nodes[v]["last"] - data.get("duracion", 0)
                     for _, v, data in grafo.out_edges(nodo, data=True)])

    shared.detalles_last.append(
        f"$L_{nodo} = Min \\{{{', '.join(partes_formula)}\\}} = "
        f"Min \\{{{', '.join(partes_valores)}\\}} = "
        f"Min \\{{{', '.join(partes_restas)}\\}} = {resultado}$"
    )

    return resultado

