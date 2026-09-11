import pandas as pd
import plotly.graph_objects as go
from cpm_extremo.output import filesystem as fs

def dibujar_gantt(df_holguras, dir: str, filename: str="output_gantt.png"):
    """
    Genera y guarda el diagrama de Gantt del proyecto a partir de la tabla de holguras óptima.

    Construye un DataFrame con la información temporal de cada actividad (inicio, duración, fin, criticidad y ruta), dibuja las barras críticas y no críticas mediante Plotly, invierte el eje vertical para el orden habitual de Gantt y configura etiquetas, colores y tooltips. Finalmente, exporta la imagen al directorio indicado.

    Parámetros
    ----------
    df_holguras : pandas.DataFrame
        Tabla con Ei, Dij, holguras y criticidad de cada actividad.
    dir : str
        Directorio donde se guardará la imagen generada.
    filename : str, opcional
        Nombre del archivo de salida (por defecto 'output_gantt.png').
    """

    datos = []
    for _, row in df_holguras.iterrows():
        inicio = row["Ei"]
        duracion = row["Dij"]

        datos.append({
            "Actividad": str(row["Actividad"]),
            "Inicio": inicio,
            "Duracion": duracion,
            "Fin": inicio + duracion,
            "Critica": row["Critica"],
            "Holgura": row["Hij"],
            "Ruta": f"{row['Nodo_i']} → {row['Nodo_j']}"
        })

    df = pd.DataFrame(datos)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df["Actividad"],
        x=df["Inicio"],
        orientation="h",
        marker=dict(color="rgba(0,0,0,0)"),
        hoverinfo="skip",
        showlegend=False,
    ))

    # Tareas críticas
    df_crit = df[df["Critica"] == True]
    fig.add_trace(go.Bar(
        y=df_crit["Actividad"],
        x=df_crit["Duracion"],
        orientation="h",
        marker=dict(color="red"),
        name="Críticas",
        customdata=df_crit[["Inicio", "Fin", "Holgura", "Ruta"]],
        hovertemplate=(
            "<b>%{y}</b><br>" +
            "Inicio: %{customdata[0]}<br>" +
            "Fin: %{customdata[1]}<br>" +
            "Holgura: %{customdata[2]}<br>" +
            "Ruta: %{customdata[3]}<br>"
        )
    ))

    # Tareas no críticas
    df_no = df[df["Critica"] == False]
    fig.add_trace(go.Bar(
        y=df_no["Actividad"],
        x=df_no["Duracion"],
        orientation="h",
        marker=dict(color="blue"),
        name="No críticas",
        customdata=df_no[["Inicio", "Fin", "Holgura", "Ruta"]],
        hovertemplate=(
            "<b>%{y}</b><br>" +
            "Inicio: %{customdata[0]}<br>" +
            "Fin: %{customdata[1]}<br>" +
            "Holgura: %{customdata[2]}<br>" +
            "Ruta: %{customdata[3]}<br>"
        )
    ))

    fig.update_yaxes(autorange="reversed")

    fig.update_layout(
        title="Diagrama de Gantt del Proyecto",
        barmode="stack",
        xaxis_title="Duración (días)",
        yaxis_title="Actividades"
    )

    fig.update_layout(
        font=dict(
            family="Arial",
            color="black",
            size=14
        )
    )

    fig.update_xaxes(
        tickmode="linear",
        dtick=1,
        tick0=0,
        ticks="outside",
        showgrid=True
    )

    # Guardar el archivo
    ruta = fs.obtener_path_completo(dir, filename)
    fig.write_image(ruta, scale=3)

