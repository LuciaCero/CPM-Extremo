import pandas as pd

def construir_estado_inicial(df_actividades: pd.DataFrame) -> pd.DataFrame:
    """
    Construye el estado inicial del proyecto a partir del DataFrame de actividades.

    Genera un DataFrame con la duración y el coste actuales de cada actividad, inicializados con sus valores normales (Dn y Cn), que servirán como base para las iteraciones del CPM extremo.

    Parámetros
    ----------
    df_actividades : pandas.DataFrame
        Tabla de actividades.

    Devuelve
    --------
    pandas.DataFrame
        Estado inicial del proyecto con duración y coste actuales.
    """


    # Creamos un nuevo df
    estado = pd.DataFrame({
        "Actividad": df_actividades["Actividad"],
        "Duracion": df_actividades["Dn"],
        "Coste": df_actividades["Cn"]
    })

    return estado
