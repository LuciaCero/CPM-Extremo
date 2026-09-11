from .algoritmo import (
    algoritmo_cpm
)

from .camino_critico import (
    obtener_actividades_criticas_reducibles,
    obtener_actividades_criticas,
    calcular_caminos_criticos
)

from .costes import (
    calcular_coste_total
)

from .duracion import (
    calcular_duracion_proyecto
)

from .early_last import (
    calcular_early_last
)

from .estado import (
    construir_estado_inicial
)
from .holguras import (
    calcular_tabla_holguras
)
from .pendientes import (
    calcular_pendientes
)
from .reduccion_actividades import (
    reducir_duracion
)

__all__ = [
    "algoritmo_cpm",
    "obtener_actividades_criticas_reducibles",
    "obtener_actividades_criticas",
    "calcular_caminos_criticos",
    "calcular_coste_total",
    "calcular_duracion_proyecto",
    "calcular_early_last",
    "construir_estado_inicial",
    "calcular_tabla_holguras",
    "calcular_pendientes",
    "reducir_duracion"
]
