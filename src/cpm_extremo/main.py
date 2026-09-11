import sys
from cpm_extremo import input
from cpm_extremo.cpm import algoritmo as cpm
from cpm_extremo import grafo as G
from cpm_extremo.output import filesystem as fs
from cpm_extremo.output import grafo_png as o_grafo
from cpm_extremo.output import coste_tiempo_png as o_coste_tiempo
from cpm_extremo.output import gantt_png as o_gantt
from cpm_extremo.output import latex_informe as o_latex


def main():
    """
    Punto de entrada del programa.

    Lee el Excel indicado por línea de comandos, construye el grafo AOA, ejecuta el
    algoritmo CPM extremo y genera todas las salidas (grafo, curva coste-tiempo,
    informe LaTeX y diagrama de Gantt) en output/<nombre_del_excel>/.
    """

    # Comprobar número de argumentos
    if len(sys.argv) != 2:
        print("Uso: python -m cpm_extremo.main <input.xlsx>")
        sys.exit(1)

    # Preparar carpeta de outputs de la ejecución
    directorio = fs.crear_carpeta_ejecucion(sys.argv[1])

    # 1. Lectura del input
    df_actividades, df_proyecto = input.leer_input(sys.argv[1])

    # 2. Crear y guardar grafo
    grafo = G.reducir_grafo(G.crear_grafo(df_actividades))
    o_grafo.dibujar_grafo(grafo, directorio)

    # 3. Ejecutar algoritmo
    historial_iteraciones, historial_coste_tiempo, idx_optima = cpm.algoritmo_cpm(grafo, df_actividades, df_proyecto)

    # 4. Crear y guardar curva coste-tiempo
    o_coste_tiempo.dibujar_coste_tiempo(historial_coste_tiempo, directorio)

    # 5. Crear y guardar LaTeX
    o_latex.generar_pert(directorio, historial_iteraciones, df_actividades, df_proyecto, historial_coste_tiempo, idx_optima)

    # 6. Crear y guardar diagrama de Gantt
    iteracion_optima = historial_iteraciones[idx_optima]
    o_gantt.dibujar_gantt(iteracion_optima["Holguras"], directorio)


if __name__ == "__main__":
    main()
