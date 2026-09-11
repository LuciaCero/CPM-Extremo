import pandas as pd
import networkx as nx
from cpm_extremo.cpm import estado
from cpm_extremo.cpm import pendientes as pendientes
from cpm_extremo.cpm import camino_critico as critico
from cpm_extremo.cpm import holguras as holguras
from cpm_extremo.cpm import duracion as duracion
from cpm_extremo.cpm import costes as costes
from cpm_extremo.cpm import early_last as early_last
from cpm_extremo.cpm import reduccion_actividades as reduccion
from cpm_extremo import shared
from cpm_extremo import grafo as G

def algoritmo_cpm(
    grafo: nx.DiGraph,
    df_actividades: pd.DataFrame,
    df_proyecto: pd.DataFrame
)-> tuple[list, list, int]:
    """
    Ejecuta el método CPM extremo sobre un grafo AOA y devuelve la evolución completa del proceso.

    El algoritmo:
    - Construye el estado inicial y calcula las pendientes de todas las actividades.
    - Itera recalculando early/last, holguras, actividades críticas, duración y coste total.
    - Selecciona la actividad crítica reducible con menor pendiente y reduce su duración.
    - Registra cada iteración junto con la curva coste-tiempo.
    - Se detiene cuando no quedan actividades reducibles o se producen dos subidas
      consecutivas de coste.

    Parámetros
    ----------
    grafo : nx.DiGraph
        Grafo AOA con duraciones iniciales.
    df_actividades : pandas.DataFrame
        Tabla de actividades con duraciones normales y extremas, costes normales y extremos y pendientes.
    df_proyecto : pandas.DataFrame
        Parámetros globales del proyecto: costes indirectos fijos y variables.

    Devuelve
    --------
    historial_iteraciones : list
        Lista de diccionarios con el estado completo de cada iteración.
    historial_coste_tiempo : list
        Pares (duración, coste) que forman la curva coste-tiempo.
    idx_optima : int
        Índice de la iteración con coste total mínimo.
    """
    
    # 1. Construir estado inicial
    df_estado = estado.construir_estado_inicial(df_actividades)

    # 2. Calcular pendientes
    df_actividades = pendientes.calcular_pendientes(df_actividades)

    # Variables para registrar los cambios
    coste_total_anterior = float("inf")
    historial_coste_tiempo = []
    historial_iteraciones = []
    subidas_consecutivas = 0
    cambio = True

    while True:

        # 3. Cálculos de la iteración
        df_early_last = early_last.calcular_early_last(grafo)
        df_holguras = holguras.calcular_tabla_holguras(grafo, df_early_last)
        act_criticas = critico.obtener_actividades_criticas(df_holguras)
        caminos_criticos = critico.calcular_caminos_criticos(grafo,act_criticas)
        duracion_total = duracion.calcular_duracion_proyecto(df_holguras, caminos_criticos)
        coste_total = costes.calcular_coste_total(df_estado, df_proyecto, duracion_total)

        # Guardar datos si ha habido cambios (evita iteraciones duplicadas si se revierte el cambio)
        if(cambio):
            historial_coste_tiempo.append((duracion_total, coste_total))
            historial_iteraciones.append({
                "Estado": df_estado.copy(),
                "Early_Last": df_early_last.copy(),
                "DetallesEarly": shared.detalles_early.copy(),
                "DetallesLast": shared.detalles_last.copy(),
                "Holguras": df_holguras.copy(),
                "DetallesHolguras": shared.detalles_holguras.copy(),
                "ActividadesCriticas": act_criticas.copy(),
                "CaminosCriticos": caminos_criticos.copy(),
                "DuracionProyecto": duracion_total,
                "DetallesDuracion": shared.detalles_duracion.copy(),
                "CosteTotal": coste_total,
                "DetallesCoste": shared.detalles_coste.copy()
            })

        # Condición de parada 1: Dos subidas consecutivas
        if coste_total > coste_total_anterior:
            subidas_consecutivas += 1
        else:
            subidas_consecutivas = 0

        if subidas_consecutivas >= 2:
            break

        coste_total_anterior = coste_total

        # 5. Seleccionar actividad crítica con menor pendiente
        actividad = critico.obtener_actividades_criticas_reducibles(df_actividades, df_estado, act_criticas)

        # Condición de parada 2: No quedan actividades reducibles
        if actividad is None:
            break

        # 6. Reducir su duración en un dia
        df_estado, cambio = reduccion.reducir_duracion(df_actividades,df_estado,duracion_total,grafo,actividad)

        # 7. Actualizar valores del grafo con las nuevas duraciones
        G.actualizar_duraciones(grafo, df_estado)

    # Guardar posición de iteración óptima
    idx_optima = min(
        range(len(historial_iteraciones)),
        key=lambda i: historial_iteraciones[i]["CosteTotal"]
    )

    return historial_iteraciones, historial_coste_tiempo, idx_optima
