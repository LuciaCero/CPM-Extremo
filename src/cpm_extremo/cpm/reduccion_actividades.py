import pandas as pd
import networkx as nx
import copy
from cpm_extremo.cpm import camino_critico as critico
from cpm_extremo.cpm import holguras as holguras
from cpm_extremo.cpm import early_last as early_last
from cpm_extremo.cpm import duracion as duracion
from cpm_extremo import grafo as G
from cpm_extremo import shared

def reducir_duracion(
        df_actividades: pd.DataFrame,
        df_estado: pd.DataFrame,
        duracion_proyecto_antes: float,
        grafo: nx.DiGraph,
        act: str
    ) -> tuple[pd.DataFrame, bool]:
    """
    Intenta reducir en un día la duración de una actividad crítica.

    Aplica la reducción de forma temporal sobre el estado y el grafo, recalcula holguras, caminos críticos y duración total, y valida si la reducción es admisible. Si la actividad alcanza un valor por debajo de su duración mínima o la reducción no produce ningún efecto útil, se marca como no reducible. Devuelve el nuevo estado y un indicador de éxito.

    Parámetros
    ----------
    df_actividades : pandas.DataFrame
        Actividades con duraciones normal/extrema, costes normales/extremos y pendientes.
    df_estado : pandas.DataFrame
        Estado actual del proyecto (duraciones y costes).
    duracion_proyecto_antes : float
        Duración total del proyecto antes de aplicar la reducción.
    grafo : nx.DiGraph
        Grafo AOA con las duraciones actuales.
    act : str
        Actividad crítica candidata a reducir.

    Devuelve
    --------
    tuple[pandas.DataFrame, bool]
        Nuevo estado tras la reducción y un booleano indicando si fue válida.
    """

    # 1. Copia del estado y del grafo
    estado_temp = df_estado.copy(deep=True)
    grafo_temp = copy.deepcopy(grafo)

    # 2. Datos iniciales
    dur_actual = estado_temp.loc[estado_temp["Actividad"] == act, "Duracion"].iloc[0]
    dur_min = df_actividades.loc[df_actividades["Actividad"] == act, "De"].iloc[0]
    coste_actual = estado_temp.loc[estado_temp["Actividad"] == act, "Coste"].iloc[0]
    pendiente = df_actividades.loc[df_actividades["Actividad"] == act, "Pendiente"].iloc[0]

    # 3. Intento de reducción
    nueva_duracion = dur_actual - 1
    nuevo_coste = coste_actual + pendiente

    # Aplicar reducción temporal
    estado_temp.loc[estado_temp["Actividad"] == act, "Duracion"] = nueva_duracion
    estado_temp.loc[estado_temp["Actividad"] == act, "Coste"] = nuevo_coste

    # Actualizar grafo temporalmente
    G.actualizar_duraciones(grafo_temp, estado_temp)

    # Recalcular holguras y caminos
    df_early_last = early_last.calcular_early_last(grafo_temp)
    df_holguras_temp = holguras.calcular_tabla_holguras(grafo_temp, df_early_last)
    act_criticas = critico.obtener_actividades_criticas(df_holguras_temp)
    caminos_criticos = critico.calcular_caminos_criticos(grafo_temp,act_criticas)
    duracion_proyecto_despues = duracion.calcular_duracion_proyecto(df_holguras_temp, caminos_criticos)

    # Limpiar
    shared.reset_early() 
    shared.reset_last()
    shared.reset_holguras()

    # Revertir cambio
    if ((nueva_duracion < dur_min) or 
        (duracion_proyecto_antes == duracion_proyecto_despues and nuevo_coste == coste_actual)):
        shared.actividades_no_reducibles.add(act)
        print(f"No se puede reducir actividad: {act}")
        return df_estado, False

    return estado_temp, True
