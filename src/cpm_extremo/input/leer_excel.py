import pandas as pd

def leer_input(nombre_excel: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Lee el archivo Excel del proyecto y construye los DataFrames estructurados necesarios para el CPM extremo.

    Extrae la información de actividades (duraciones, costes y dependencias) y los parámetros globales del proyecto, devolviéndolos en dos DataFrames separados para facilitar los cálculos posteriores.

    Parámetros
    ----------
    nombre_excel : str
        Ruta del archivo Excel de entrada.

    Devuelve
    --------
    tuple[pandas.DataFrame, pandas.DataFrame]
        DataFrame de actividades y DataFrame con parámetros del proyecto.
    """

    # Leer el excel
    df = pd.read_excel(nombre_excel)

    # Identificar numero de tareas
    fila_Dn = df.iloc[0, 1:]
    nTareas = fila_Dn.count()

    # Crear DataFrames
    df_actividades = _crear_df_actividades(df, fila_Dn, nTareas)
    df_proyecto =_crear_df_proyecto(df)

    return df_actividades, df_proyecto

def _crear_df_actividades(df: pd.DataFrame, fila_Dn: list, nTareas: int) -> pd.DataFrame:
    """
    Construye el DataFrame de actividades a partir del Excel original.

    Extrae nombres de actividades, duraciones normal/extrema, costes normal/crash y dependencias. También calcula los sucesores a partir de los predecesores para completar la estructura necesaria para el grafo AOA.

    Parámetros
    ----------
    df : pandas.DataFrame
        Datos completos leídos del Excel.
    fila_Dn : list
        Fila que contiene las duraciones normales.
    nTareas : int
        Número total de actividades del proyecto.

    Devuelve
    --------
    pandas.DataFrame
        Tabla estructurada de actividades con duraciones, costes y dependencias.
    """

    # Crear dataframe de actividades
    df_actividades = pd.DataFrame(columns=["Actividad", "Predecesor", "Sucesor", "Dn", "De", "Cn", "Ce"])
    # Numeros de filas
    nFila_Dn = 0
    nFila_De = 1
    nFila_Cn = 4
    nFila_Ce = 5
    nFila_Dependencias = 10
    # Obtener valores de cada fila
    actividades = df.columns[1:nTareas+1]
    Dn = df.iloc[nFila_Dn, 1:nTareas+1]
    De = df.iloc[nFila_De, 1:nTareas+1]
    Cn = df.iloc[nFila_Cn, 1:nTareas+1].astype(float)
    Ce = df.iloc[nFila_Ce, 1:nTareas+1].astype(float)
    # Añadir valores al df creado
    df_actividades["Actividad"] = actividades
    df_actividades["Dn"] = Dn.values
    df_actividades["De"] = De.values
    df_actividades["Cn"] = Cn.values
    df_actividades["Ce"] = Ce.values
    # Obtener dependencias
    tabla_dep = df.iloc[nFila_Dependencias+1 : nFila_Dependencias+1+nTareas, 0:nTareas+1]
    tabla_dep.columns = df.iloc[nFila_Dependencias, 0:nTareas+1]
    tabla_dep = tabla_dep.set_index("Dependencias")
    predecesores = []
    for act in actividades:
        col = tabla_dep[act]
        # Añade las filas con 1
        preds = col[col == 1].index.tolist()
        predecesores.append(preds)
    df_actividades["Predecesor"] = predecesores
    # Añadir sucesores
    df_actividades = _agregar_sucesores(df_actividades)

    return df_actividades

def _agregar_sucesores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula la lista de sucesores de cada actividad a partir de sus predecesores.

    Recorre todas las actividades y construye el conjunto inverso de dependencias, añadiéndolo como una nueva columna en el DataFrame.

    Parámetros
    ----------
    df : pandas.DataFrame
        Actividades con su lista de predecesores.

    Devuelve
    --------
    pandas.DataFrame
        Mismo DataFrame con la columna 'Sucesor' añadida.
    """
    
    # Inicializamos el diccionario de sucesores
    sucesores = {act: [] for act in df["Actividad"]}

    # Recorremos cada fila
    for _, row in df.iterrows():
        actividad = row["Actividad"]
        for pred in row["Predecesor"]:
            sucesores[pred].append(actividad)

    # Añadimos la columna al df
    df["Sucesor"] = df["Actividad"].map(sucesores)

    return df

def _crear_df_proyecto(df: pd.DataFrame) -> pd.DataFrame:
    """
    Construye el DataFrame con los parámetros globales del proyecto.

    Extrae el coste indirecto fijo y el coste indirecto diario desde las filas correspondientes del Excel, sustituyendo valores vacíos por cero.

    Parámetros
    ----------
    df : pandas.DataFrame
        Datos completos leídos del Excel.

    Devuelve
    --------
    pandas.DataFrame
        Tabla con los parámetros del proyecto (costes indirectos).
    """
    
    # Crear dataframe del proyecto
    df_proyecto = pd.DataFrame(columns=["C_indirecto", "C_indirecto_diario"])
    # Numero de fila
    nFila_Ci = 8
    # Obtener valores de la fila
    Ci = df.iloc[nFila_Ci, 1:3]
    # Reemplazar NaN por 0
    Ci_numeros = [float(x) if pd.notna(x) else 0 for x in Ci]
    # Añadir valores
    df_proyecto.loc[len(df_proyecto)] = Ci_numeros

    return df_proyecto