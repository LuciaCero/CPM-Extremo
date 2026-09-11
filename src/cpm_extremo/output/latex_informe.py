import pandas as pd
from cpm_extremo.output import filesystem as fs

def generar_pert(
    dir: str,
    historial: list,
    df_actividades: pd.DataFrame,
    df_proyecto: pd.DataFrame,
    historial_coste_tiempo: list,
    idx_optima: int,
    filename: str="output_pert.txt"
):
    """
    Genera un informe PERT completo en formato LaTeX.

    Construye el documento incluyendo los datos del proyecto, todas las iteraciones del CPM extremo (estado, early/last, holguras, caminos críticos, duración y coste) y la curva coste-tiempo. Ensambla el contenido en un archivo .tex dentro del directorio indicado.

    Parámetros
    ----------
    dir : str
        Carpeta donde se guardará el archivo generado. historial : list
        Lista de iteraciones completas del CPM extremo.
    df_actividades : pandas.DataFrame
        Tabla de actividades con duraciones, costes y dependencias.
    df_proyecto : pandas.DataFrame
        Parámetros globales del proyecto.
    historial_coste_tiempo : list
        Lista de pares (duración, coste) para la curva coste-tiempo.
    idx_optima : int
        Índice de la iteración óptima.
    filename : str, opcional
        Nombre del archivo LaTeX de salida.
    """

    # Datos iniciales
    cabecera = "\\documentclass{llncs}\n\\usepackage{fullpage}\n\\usepackage{graphicx}\n\\usepackage{array}\n\\usepackage[utf8]{inputenc}\n\\usepackage{amsmath}\n\\usepackage{mathtools}\n\\usepackage{siunitx}\n\\usepackage{tikz}\n\\usetikzlibrary{arrows.meta, positioning}\n\\usepackage{pgfplots}\n\\pgfplotsset{compat=1.18}\n\\renewcommand{\\arraystretch}{1.5}\n\\setlength{\\tabcolsep}{6pt}"
    cabecera += "\n\\begin{document}\n\n"
    final = "\\end{document}"
    contenido = ""

    # Datos proyecto
    contenido += _latex_datos_actividades(df_actividades)
    contenido += _latex_datos_proyecto(df_proyecto)

    # Iteraciones
    for i, it in enumerate(historial, start=0):
        contenido += _latex_iteracion(it, i, idx_optima)

    contenido += "\\newpage\n\n"  
    contenido += _generar_latex_coste_tiempo(historial_coste_tiempo)

    # Guardar archivo
    ruta = fs.obtener_path_completo(dir, filename)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(cabecera)
        f.write(contenido)
        f.write(final)

def _latex_datos_actividades(df_actividades: pd.DataFrame) -> str:
    """
    Genera la tabla LaTeX con los datos de todas las actividades.
    """
    
    contenido = "\\section*{Datos de las Actividades}\n"
    contenido += "\\noindent\n"
    contenido += "\\begin{tabular}{|c|c|c|c|c|c|c|c|}\n"
    contenido += "\\hline\n"
    contenido += "Actividad & Predecesor & Sucesor & $D_n$ & $D_e$ & $C_n$ & $C_e$ & Pendiente \\\\\n"
    contenido += "\\hline\n"

    for _, row in df_actividades.iterrows():
        pred = _format_lista(row["Predecesor"])
        succ = _format_lista(row["Sucesor"])

        contenido += (
            f"{row['Actividad']} & "
            f"{pred} & "
            f"{succ} & "
            f"{row['Dn']} & "
            f"{row['De']} & "
            f"{row['Cn']} & "
            f"{row['Ce']} & "
            f"{row['Pendiente']} \\\\\n"
        )

    contenido += "\\hline\n"
    contenido += "\\end{tabular}\n\n"

    return contenido

def _format_lista(valor):
    """
    Da formato a la lista de predecesores y sucesores, poniéndolos entre "[]"
    """

    if isinstance(valor, list):
        return "[" + ", ".join(valor) + "]" if valor else "[]"
    if valor in (None, "", float("nan")):
        return "[]"
    return f"[{valor}]"

def _latex_datos_proyecto(df_proyecto: pd.DataFrame) -> str:
    """
    Genera la tabla LaTeX con los parámetros globales del proyecto.

    Incluye el coste indirecto fijo y el coste indirecto diario.
    """
    
    contenido = "\\section*{Datos del Proyecto}\n"
    contenido += "\\noindent\n"

    contenido += "\\begin{tabular}{|c|c|}\n"
    contenido += "\\hline\n"
    contenido += "Coste Indirecto Fijo & Coste Indirecto Diario \\\\\n"
    contenido += "\\hline\n"
    row = df_proyecto.iloc[0]
    contenido += f"{row['C_indirecto']} & {row['C_indirecto_diario']} \\\\\n"
    contenido += "\\hline\n"
    contenido += "\\end{tabular}\n\n" 

    return contenido   

def _latex_estado(it: list) -> str:
    """
    Genera la tabla LaTeX del estado de actividades en una iteración.

    Muestra la duración y el coste actual de cada actividad.
    """

    contenido = "\\subsection*{Estado de actividades}\n\\noindent\n"
    contenido += "\\begin{tabular}{|c|c|c|}\n"
    contenido += "\\hline\nActividad & Duración (días) & Coste (\\text{€}) \\\\\n\\hline\n"

    df = it["Estado"]
    for _, row in df.iterrows():
        contenido += f"{row['Actividad']} & {row['Duracion']} & {row['Coste']} \\\\\n"

    contenido += "\\hline\\end{tabular}\n\n"

    return contenido

def _latex_early_last(it: list) -> str:
    """
    Genera la tabla LaTeX con los valores Early y Last de cada nodo.
    """

    contenido = "\\subsection*{Tabla Early/Last}\n\\noindent\n"
    contenido += "\\begin{tabular}{|c|c|c|}\n"
    contenido += "\\hline\nNodo & Early & Last \\\\\n\\hline\n"

    df = it["Early_Last"]
    for _, row in df.iterrows():
        contenido += f"{row['Nodo']} & {row['Early']} & {row['Last']} \\\\\n"

    contenido += "\\hline\n\\end{tabular}\n\n"

    return contenido

def _latex_detalles_early(it: list) -> str:
    """
    Genera el bloque LaTeX con los detalles del cálculo Early.
    """

    contenido = "\\subsection*{Detalles Early}\n\\noindent\n"

    for linea in it["DetallesEarly"]:
        contenido += f"{linea}\\\\\n"

    contenido += "\n"

    return contenido

def _latex_detalles_last(it: list) -> str:
    """
    Genera el bloque LaTeX con los detalles del cálculo Last.
    """

    contenido = "\\subsection*{Detalles Last}\n\\noindent\n"

    for linea in it["DetallesLast"]:
        contenido += f"{linea}\\\\\n"
    
    contenido += "\n"

    return contenido

def _latex_holguras(it: list) -> str:
    """
    Genera la tabla LaTeX con las holguras de cada actividad.

    Incluye Actividad, ruta i→j, duración, Early_i, Last_j, holgura y criticidad.
    """

    contenido = "\\subsection*{Tabla de Holguras}\n"
    contenido += "\\noindent\n"

    contenido += "\\begin{tabular}{|c|c|c|c|c|c|c|}\n"
    contenido += "\\hline\n"
    contenido += (
        "Tarea & Ruta($i \\rightarrow j$) & "
        "$Duracion_{ij}$ & $Early_i$ & $Last_j$ & "
        "$Holgura_{ij}$ & Crítica \\\\\n"
    )
    contenido += "\\hline\n"

    df = it["Holguras"]
    for _, row in df.iterrows():
        critica = "Sí" if row["Critica"] else "No"
        ruta = f"{row['Nodo_i']} $\\rightarrow$ {row['Nodo_j']}"
        contenido += (
            f"{row['Actividad']} & "
            f"{ruta} & "
            f"{row['Dij']} & "
            f"{row['Ei']} & "
            f"{row['Lj']} & "
            f"{row['Hij']} & "
            f"{critica} \\\\\n"
        )

    contenido += "\\hline\n"
    contenido += "\\end{tabular}\n\n"

    return contenido

def _latex_detalles_holguras(it: list) -> str:
    """
    Genera el bloque LaTeX con los detalles del cálculo de holguras.
    """

    contenido = "\\subsection*{Detalles de Holguras}\n"
    contenido += "\\noindent\n"

    for linea in it["DetallesHolguras"]:
        contenido += linea + "\\\\\n"

    contenido += "\n"

    return contenido

def _generar_caminos_criticos(it: list) -> str:
    """
    Genera el bloque LaTeX con las actividades críticas y los caminos críticos.
    """

    contenido = "\\subsection*{Caminos Críticos}\n"
    contenido += "\\noindent\n"

    # Actividades críticas
    contenido += "Actividades críticas: "
    contenido += ", ".join(it["ActividadesCriticas"])
    contenido += "\\\\[6pt]\n"

    # Caminos críticos
    for idx, camino in enumerate(it["CaminosCriticos"], start=1):
        camino_str = " $\\rightarrow$ ".join(str(n) for n in camino)
        contenido += f"Camino\\ crítico\\ {idx}:\\ {camino_str}\\\\\n"

    return contenido

def _latex_duracion(it) -> str:
    """
    Genera el bloque LaTeX con la duración total del proyecto en la iteración.
    """

    dur = it["DuracionProyecto"]
    contenido = f"\\subsection*{{Duración del proyecto:}}\n\\noindent\n{dur} días\\\\\n"
    return contenido

def _latex_detalles_duracion(it):
    """
    Genera el bloque LaTeX con los detalles del cálculo de la duración.
    """

    contenido = "\\subsection*{Detalles del cálculo de la duración}\n\\noindent\n"
    for linea in it["DetallesDuracion"]:
        contenido += f"{linea}\\\\\n"
    contenido += "\n"
    return contenido

def _latex_coste(it) -> str:
    """
    Genera el bloque LaTeX con el coste total del proyecto en la iteración.
    """

    coste = it["CosteTotal"]
    contenido = f"\\subsection*{{Coste total del proyecto:}}\n\\noindent\n{coste} \\text{{€}}\\\\\n"
    return contenido

def _latex_detalles_coste(it):
    """
    Genera el bloque LaTeX con los detalles del cálculo del coste.
    """

    contenido = "\\subsection*{Detalles del cálculo del coste}\n\\noindent\n"
    for linea in it["DetallesCoste"]:
        contenido += f"{linea}\\\\\n"
    contenido += "\n"
    return contenido

def _latex_iteracion(it: list, num_iter: int, idx_optima: int) -> str:
    """
    Genera el contenido LaTeX de una iteración.
    """
    contenido = "\\newpage\n\n"

    if num_iter < idx_optima:
        contenido += f"\\section*{{Iteración {num_iter+1}}}\n\n"
    elif num_iter == idx_optima:
        contenido += f"\\section*{{Iteración {num_iter+1} (óptima)}}\n\n"
    else:
        contenido += f"\\section*{{Iteración {num_iter+1} (extra)}}\n\n"

    contenido += _latex_estado(it)
    contenido += _latex_early_last(it)
    contenido += _latex_detalles_early(it)
    contenido += _latex_detalles_last(it)
    contenido += _latex_holguras(it)
    contenido += _latex_detalles_holguras(it)
    contenido += _generar_caminos_criticos(it)
    contenido += _latex_duracion(it)
    contenido += _latex_detalles_duracion(it)
    contenido += _latex_coste(it)
    contenido += _latex_detalles_coste(it)
    
    return contenido

def _generar_latex_coste_tiempo(historial: list) -> str:
    """
    Genera el bloque LaTeX con la curva coste-tiempo usando TikZ/PGFPlots.

    Ordena las iteraciones por duración, construye las coordenadas de la curva, identifica el punto óptimo y genera el código completo para dibujar la gráfica en el documento PERT.
    """

    # Ordenar por duración de mayor a menor (como tu PNG)
    historial = sorted(historial, key=lambda x: x[0], reverse=True)

    # Extraer duraciones y costes
    duraciones = [h[0] for h in historial]
    costes = [h[1] for h in historial]

    # Encontrar punto óptimo (mínimo coste, y si hay empate, menor duración)
    coste_min = min(costes)
    indices_coste_min = [i for i, c in enumerate(costes) if c == coste_min]
    idx_min = min(indices_coste_min, key=lambda i: duraciones[i])
    duracion_optima = duraciones[idx_min]

    # Construir coordenadas para \addplot
    coords = "\n        ".join(f"({d},{c})" for d, c in zip(duraciones, costes))

    # Cadena TikZ completa
    cadena = f"""
\\section*{{Curva Coste--Tiempo}}
\\begin{{center}}
\\begin{{tikzpicture}}
\\begin{{axis}}[
    xlabel={{Duración del proyecto (días)}},
    ylabel={{Coste total (€)}},
    title={{Curva Coste-Tiempo del Proyecto}},
    grid=both,
    grid style={{dashed, gray!30}},
    x dir=reverse,
    enlargelimits=0.1,
    width=12cm,
    height=8cm,
]

% Curva coste-tiempo
\\addplot[
    color=blue,
    mark=*,
    thick
] coordinates {{
        {coords}
}};

% Punto óptimo
\\addplot[
    color=red,
    mark=*,
    only marks
] coordinates {{
    ({duracion_optima},{coste_min})
}};

% Anotación del punto óptimo
\\node at (axis cs:{duracion_optima},{coste_min}) [below right] {{$({{{duracion_optima}}}\\text{{ días}},\\ {{{coste_min}}}\\text{{€}})$}};

\\end{{axis}}
\\end{{tikzpicture}}
\\end{{center}}
"""

    return cadena
