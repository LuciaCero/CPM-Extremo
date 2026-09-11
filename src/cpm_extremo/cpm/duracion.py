import pandas as pd
from cpm_extremo import shared

def calcular_duracion_proyecto(df_holgura: pd.DataFrame, caminos_criticos: list) -> float:
    """
    Calcula la duración total del proyecto a partir de los caminos críticos.

    Para cada camino crítico, suma las duraciones de sus actividades según la tabla de holguras y registra la fórmula simbólica y numérica utilizada para añadirlos a la salida output_pert.txt. La duración del proyecto se define como la mayor duración entre todos los caminos críticos evaluados.

    Parámetros
    ----------
    df_holgura : pandas.DataFrame
        Tabla con duraciones Dij y holguras de cada actividad.
    caminos_criticos : list
        Lista de caminos críticos, cada uno como lista de actividades.

    Devuelve
    --------
    float
        Duración total del proyecto (máximo de los caminos críticos).
    """


    shared.reset_duracion()
    duraciones_caminos = []

    for idx, camino in enumerate(caminos_criticos, start=1):

        # Actividades del camino
        actividades = camino

        # Duraciones de cada actividad
        duraciones = df_holgura.loc[
            df_holgura["Actividad"].isin(actividades), "Dij"
        ].tolist()

        # Duración total del camino
        duracion_camino = sum(duraciones)
        duraciones_caminos.append(duracion_camino)

        # Fórmula simbólica: A + C + F
        simbolica = " + ".join(actividades)

        # Fórmula numérica: 5 + 3 + 1
        numerica = " + ".join(str(d) for d in duraciones)

        # Línea estilo holguras
        formula = (
            f"$D_{{camino\\ {idx}}} = {simbolica} = {numerica} = {duracion_camino}$\\\\"
        )

        shared.detalles_duracion.append(formula)

    # Duración del proyecto = máximo de los caminos críticos
    return max(duraciones_caminos)