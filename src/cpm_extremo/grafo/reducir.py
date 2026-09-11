import networkx as nx

def reducir_grafo(grafo: nx.DiGraph) -> nx.DiGraph:
    """
    Simplifica el grafo AOA eliminando actividades ficticias y nodos redundantes.

    Unifica nodos ficticios equivalentes, elimina nodos ficticios innecesarios mediante fusiones sucesivas y finalmente reindexa los nodos y renumera las actividades ficticias para obtener un grafo limpio y consistente.

    Parámetros
    ----------
    grafo : nx.DiGraph
        Grafo AOA con actividades reales y ficticias.

    Devuelve
    --------
    nx.DiGraph
        Grafo reducido y renumerado.
    """

    # 1. Primero se realiza una pasada
    _unificar_nodos_ficticios_equivalentes(grafo)

    # 2. Repetir mientras se puedan eliminar nodos
    cambios = True
    while cambios:
        cambios = False
        for nodo in list(grafo.nodes):
            # if nodo in grafo.nodes:  # Puede haber sido eliminado
            if _eliminar_ficticias(grafo, nodo):
                cambios = True

    # 3. Reindexar nodos
    grafo = nx.convert_node_labels_to_integers(grafo, first_label=1, ordering='sorted')

    # 4. Renumerar actividades ficticias
    _renumerar_ficticias(grafo)

    return grafo

def _unificar_nodos_ficticios_equivalentes(grafo: nx.DiGraph):
    """
    Unifica nodos ficticios que comparten exactamente el mismo conjunto de predecesores ficticios.

    Agrupa nodos con entradas ficticias idénticas y fusiona cada grupo en un único nodo base, redirigiendo sus sucesores antes de eliminar los nodos duplicados.

    Parámetros
    ----------
    grafo : nx.DiGraph
        Grafo AOA a simplificar.
    """


    # 1. Agrupar nodos por su conjunto de predecesores ficticios
    grupos = {}  # clave = frozenset(predecesores), valor = lista de nodos

    for nodo in grafo.nodes:
        preds = list(grafo.predecessors(nodo))

        # Solo consideramos nodos cuyas entradas son todas ficticias
        if preds and all(grafo.edges[(p, nodo)].get("ficticia", False) for p in preds):
            clave = frozenset(preds)
            grupos.setdefault(clave, []).append(nodo)

    # 2. Para cada grupo con más de un nodo, unificarlos
    for _, nodos_equivalentes in grupos.items():
        if len(nodos_equivalentes) <= 1:
            continue

        # Elegimos el primer nodo como nodo baseS
        base = nodos_equivalentes[0]

        # Redirigir sucesores del nodo hacia el nodo base
        for nodo in nodos_equivalentes[1:]:
            for succ in list(grafo.successors(nodo)):
                # Copiar atributos de la arista
                attrs = grafo.edges[(nodo, succ)]
                grafo.add_edge(base, succ, **attrs)

            # Eliminar el nodo duplicado
            grafo.remove_node(nodo)

def _eliminar_ficticias(grafo: nx.DiGraph, nodo: int) -> bool:
    """
    Elimina un nodo ficticio si todas sus entradas son ficticias y tiene como máximo una salida.

    Si cumple las condiciones, fusiona el nodo con sus predecesores mediante "_unir_nodos". Devuelve True si se realizó alguna fusión.

    Parámetros
    ----------
    grafo : nx.DiGraph
        Grafo AOA en proceso de reducción.
    nodo : int
        Nodo candidato a eliminar.

    Devuelve
    --------
    bool
        True si el nodo fue fusionado; False en caso contrario.
    """

    in_edges = list(grafo.in_edges(nodo, data=True))
    if not in_edges:
        return False

    # Revisar si todas las entradas son ficticias
    if all(d.get("ficticia", False) for _, _, d in in_edges):
        for prev, _, _ in in_edges:
            _unir_nodos(grafo, prev, nodo)
        return True
    
    return False

def _unir_nodos(grafo: nx.DiGraph, prev: int, target: int):
    """
    Fusiona el nodo "prev" dentro de "target", redirigiendo todas sus aristas entrantes y salientes, y eliminando después el nodo original.

    Solo se ejecuta si "_puede_unir" confirma que la operación es válida.

    Parámetros
    ----------
    grafo : nx.DiGraph
        Grafo AOA en proceso de reducción.
    prev : int
        Nodo que será absorbido.
    target : int
        Nodo que absorberá a "prev".
    """

    if (not _puede_unir(grafo, prev, target)):
        return

    # 1. Redirigir todas las actividades entrantes de prev hacia target
    for u, _, data in list(grafo.in_edges(prev, data=True)):
        # Evitar bucles
        if u != target:  
            grafo.add_edge(u, target, **data)

    # 2. Pasar actividades salientes de prev a target
    for _, v, data in list(grafo.out_edges(prev, data=True)):
        # Evitar bucles
        if v != target:  # Evitar bucles
            grafo.add_edge(target, v, **data)

    # 3. Eliminar nodo prev
    grafo.remove_node(prev)

def _puede_unir(grafo: nx.DiGraph, prev: int, target: int) -> bool:
    """
    Determina si el nodo "prev" puede fusionarse dentro de "target".

    La fusión solo es válida si:
    - No comparten predecesores.
    - "prev" tiene exactamente una salida.
    - No se generan bucles.

    Parámetros
    ----------
    grafo : nx.DiGraph
        Grafo AOA en proceso de reducción.
    prev : int
        Nodo candidato a fusionarse.
    target : int
        Nodo destino.

    Devuelve
    --------
    bool
        True si la fusión es válida; False en caso contrario.
    """

    # 1. Revisar predecesores compartidos
    pred_prev = set(grafo.predecessors(prev))
    pred_target = set(grafo.predecessors(target))
    if pred_prev & pred_target:
        # Comparten un nodo previo, no se pueden unir
        return False

    # 2. Revisar salidas de prev
    out_prev = list(grafo.successors(prev))

    # Si no tiene salidas o tiene mas de una, no se une
    if (not out_prev) or (len(out_prev) > 1):
        return False
    
    return True

def _renumerar_ficticias(grafo: nx.DiGraph):
    """
    Renumera todas las actividades ficticias del grafo como F_1, F_2, F_3...

    Ordena las aristas ficticias por sus nodos para garantizar un renombrado estable y reproducible, y asigna identificadores consecutivos.

    Parámetros
    ----------
    grafo : nx.DiGraph
        Grafo AOA ya reducido.
    """

    # 1. Obtener todas las aristas ficticias
    ficticias = []
    for u, v, data in grafo.edges(data=True):
        if data.get("ficticia", False):
            ficticias.append((u, v, data))

    # 2. Ordenarlas para que el renombrado sea estable y reproducible
    ficticias.sort(key=lambda x: (x[0], x[1]))

    # 3. Renombrar secuencialmente
    for idx, (u, v, data) in enumerate(ficticias, start=1):
        data["actividad"] = f"F_{idx}"
