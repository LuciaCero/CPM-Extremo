import networkx as nx
from networkx.drawing.nx_agraph import to_agraph
from cpm_extremo.output import filesystem as fs

def dibujar_grafo(grafo: nx.DiGraph, dir: str, filename: str="output_graph.png"):
    """
    Genera y guarda la representación visual del grafo AOA del proyecto.

    Verifica que el grafo sea acíclico, lo convierte a formato AGraph y aplica un diseño orientado de izquierda a derecha. Configura estilos de nodos y aristas, diferenciando actividades reales y ficticias mediante colores y trazos. Finalmente renderiza el grafo con Graphviz y guarda la imagen en el directorio indicado.

    Parámetros
    ----------
    grafo : nx.DiGraph
        Grafo AOA con actividades reales y ficticias.
    dir : str
        Directorio donde se guardará la imagen generada.
    filename : str, opcional
        Nombre del archivo de salida (por defecto 'output_graph.png').
    """
    
    # Comprueba que no sea cíclico el grafo
    if not nx.is_directed_acyclic_graph(grafo):
        raise ValueError("El grafo no es acíclico")
    
    # Convertir NetworkX en AGraph
    A = to_agraph(grafo)
    
    # Layout
    A.graph_attr.update(
        rankdir="LR",
        splines="spline",
        nodesep="0.8",
        ranksep="1.0",
        pad="0.7",
        label="Grafo del Proyecto (AOA)",
        labelloc="t",
        labeljust="c",
        fontsize="16",
        fontname="Helvetica"
    )

    # Título
    A.graph_attr["label"] = "Grafo del Proyecto (AOA)\n\n"
    A.graph_attr["fontsize"] = "16"
    A.graph_attr["fontname"] = "Arial" 
    
    # Estilo de nodos
    A.node_attr.update(
        shape="circle",
        style="filled",
        fillcolor="lightblue",
        color="black",
        fontname="Helvetica",
        fontsize="14",
        width="0.5",
        height="0.5"
    )
    
    # Estilo de edges según tipo
    for u, v, d in grafo.edges(data=True):
        edge = A.get_edge(u, v)
        edge.attr["label"] = d.get("actividad", "")
        if d.get("ficticia", False):
            edge.attr.update(
                style="dashed",
                color="gray",
                penwidth="1.5",
                arrowsize="0.7"
            )
        else:
            edge.attr.update(
                style="solid",
                color="black",
                penwidth="2.0",
                arrowsize="1.0"
            )
    
    # Renderizar y guardar
    A.layout(prog="dot")

    # Guarda el archivo
    ruta = fs.obtener_path_completo(dir, filename)
    A.draw(ruta, format="png", prog="dot", args="-Gdpi=300")
