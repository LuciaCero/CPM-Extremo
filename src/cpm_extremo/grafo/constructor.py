import sys
import pandas as pd
import networkx as nx

def crear_grafo(df: pd.DataFrame) -> nx.DiGraph:
    """
    Construye el grafo AOA del proyecto a partir del DataFrame de actividades.

    Genera un grafo dirigido donde cada actividad real se representa como una arista con duración, y se añaden actividades ficticias cuando es necesario para resolver convergencias o asegurar un único nodo final. También valida previamente que las dependencias no formen ciclos.

    Parámetros
    ----------
    df : pandas.DataFrame
        Actividades del proyecto con columnas de predecesores y sucesores.

    Devuelve
    --------
    nx.DiGraph
        Grafo AOA completo con actividades reales y ficticias.
    """

    # Se valida si el grafo no contiene ciclos
    try:
        _validar_dependencias(df)
    except Exception as e:
        print("ERROR:", e)
        sys.exit(1)

    grafo = nx.DiGraph()
    nodo = 1        # Nodo inicial
    inicio = nodo
    fin = {}
    act_ficticias = 1   # Cuenta del numero de actividades ficticias

    # Añadir actividades sin predecesores
    for _, row in df.iterrows():
        act = row["Actividad"]  # Tarea actual
        duracion = row["Dn"]    # Duracion de la tarea
        # Filtrar actividades que no tengan predecesores
        if row["Predecesor"] == []:
            nodo += 1
            grafo.add_edge(inicio, nodo, actividad=act, ficticia=False, duracion=duracion) 
            fin[act] = nodo
            
    # Añadir actividades con predecesores
    for _, row in df.iterrows():
        act = row["Actividad"]
        duracion = row["Dn"]    # Duracion de la tarea

        if row["Predecesor"] != []:
            preds = row["Predecesor"]
            nodos_pred = {fin[p] for p in preds}

            # Caso 1: todos confluyen en el mismo nodo
            if len(nodos_pred) == 1:
                nodo_inicio = nodos_pred.pop()

            # Caso 2: crear nodo ficticio de convergencia
            else:
                nodo += 1
                nodo_inicio = nodo
                for n in nodos_pred:
                    grafo.add_edge(n, nodo_inicio, actividad=f"F_{act_ficticias}", ficticia=True, duracion=0)
                    act_ficticias += 1

            # Crear actividad real
            nodo += 1
            grafo.add_edge(nodo_inicio, nodo, actividad=act, ficticia=False, duracion=duracion)
            fin[act] = nodo

    # Asegurar nodo final unico
    nodo_final = nodo + 1
    nodos_finales = [fin[row["Actividad"]] for _, row in df.iterrows() if row["Sucesor"] == []]

    for n in nodos_finales:
        grafo.add_edge(n, nodo_final, actividad=f"F_{act_ficticias}", ficticia=True, duracion=0)
        act_ficticias += 1

    return grafo

def _validar_dependencias(df: pd.DataFrame):
    """
    Verifica que las dependencias del proyecto no formen ciclos.

    Construye un grafo de dependencias entre actividades y comprueba que sea acíclico. Si se detecta un ciclo, lanza una excepción con información detallada del mismo.

    Parámetros
    ----------
    df : pandas.DataFrame
        Actividades del proyecto con su lista de predecesores.

    Excepciones
    -----------
    ValueError
        Si se detectan dependencias cíclicas.
    """

    g = nx.DiGraph()

    for _, row in df.iterrows():
        act = row["Actividad"]
        g.add_node(act)
        for pred in row["Predecesor"]:
            g.add_edge(pred, act)

    if not nx.is_directed_acyclic_graph(g):
        ciclo = nx.find_cycle(g, orientation="original")
        raise ValueError(f"Dependencias cíclicas detectadas: {ciclo}")
