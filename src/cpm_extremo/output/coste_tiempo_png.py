import matplotlib.pyplot as plt
from cpm_extremo.output import filesystem as fs

def dibujar_coste_tiempo(historial, dir: str, filename: str="output_coste-tiempo.png"):
    """
    Genera y guarda la curva coste-tiempo del proyecto.

    Ordena las iteraciones por duración, dibuja la curva coste-tiempo, identifica el punto óptimo (coste mínimo con menor duración asociada), lo resalta en la gráfica y ajusta automáticamente la posición del texto para evitar solapamientos. Finalmente guarda la figura en la carpeta indicada.

    Parámetros
    ----------
    historial : list
        Lista de pares (duración, coste) generados por el CPM extremo.
    dir : str
        Directorio donde se guardará la imagen.
    filename : str, opcional
        Nombre del archivo de salida (por defecto 'output_coste-tiempo.png').
    """


    # Ordenar por duración de mayor a menor
    historial = sorted(historial, key=lambda x: x[0], reverse=True)

    # Extraer duraciones y costes
    duraciones = [h[0] for h in historial]
    costes = [h[1] for h in historial]

    # Encontrar el punto óptimo
    coste_min = min(costes)
    indices_coste_min = [i for i, c in enumerate(costes) if c == coste_min]
    idx_min = min(indices_coste_min, key=lambda i: duraciones[i])
    duracion_optima = duraciones[idx_min]

    # Crear figura
    plt.figure()
    plt.rcParams["font.family"] = "Arial"

    # Dibujar curva
    plt.plot(duraciones, costes, marker='o', color="#2a4d8f")

    # Marcar el punto óptimo
    plt.scatter(duracion_optima, coste_min, color='red', zorder=5)

    # Invertir eje x
    ax = plt.gca()
    ax.invert_xaxis()

    # Ajuste automático del texto
    fig = plt.gcf()
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    texto = f"({duracion_optima} días, {coste_min}€)"
    # Desplazamiento por defecto (en puntos tipográficos)
    dx, dy = 6, -8
    # Convertir desplazamiento a píxeles
    dpi = fig.dpi
    dx_px = dx * dpi / 72
    # Coordenadas del punto en pantalla
    x_disp, y_disp = ax.transData.transform((duracion_optima, coste_min))
    # Medir ancho real del texto
    t = plt.text(0, 0, texto, fontsize=10)
    bbox_text = t.get_window_extent(renderer=renderer)
    t.remove()
    ancho_texto = bbox_text.width
    # Borde derecho real del área de datos
    borde_derecho = ax.bbox.x1
    # Borde derecho del texto si se dibuja a la derecha
    borde_texto_derecha = x_disp + dx_px + ancho_texto
    # Si se sale → mover a la izquierda
    if borde_texto_derecha > borde_derecho:
        dx = - (ancho_texto / (dpi/72) + 6)

    # Dibujar texto definitivo
    plt.annotate(
        texto,
        xy=(duracion_optima, coste_min),
        xytext=(dx, dy),
        textcoords="offset points",
        fontsize=10,
        color="black"
    )

    # Etiquetas
    plt.xlabel("Duración del proyecto (días)")
    plt.ylabel("Coste total (€)")
    plt.title("Curva Coste-Tiempo del Proyecto", fontsize=16, pad=30)

    # Fondo
    plt.grid(True, linestyle="--", linewidth=0.5, color="#cccccc")

    # Guardar archivo
    ruta = fs.obtener_path_completo(dir, filename)
    plt.savefig(ruta, dpi=300, bbox_inches='tight', pad_inches=1)
