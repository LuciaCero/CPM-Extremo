"""
Variables compartidas para el análisis CPM.
"""

detalles_early: list = []
detalles_last: list = []
detalles_holguras: list = []
actividades_no_reducibles = set()
detalles_duracion: list = []
detalles_coste: list = []

def reset_early():
    """
    Limpia la lista de detalles del cálculo Early.

    Se utiliza antes de generar una nueva tabla Early/Last para evitar que queden restos de iteraciones anteriores.
    """

    detalles_early.clear()

def reset_last():
    """
    Limpia la lista de detalles del cálculo Last.

    Se utiliza antes de generar una nueva tabla Early/Last para evitar que queden restos de iteraciones anteriores.
    """

    detalles_last.clear()

def reset_holguras():
    """
    Limpia la lista de detalles del cálculo de holguras.

    Se ejecuta antes de recalcular holguras para asegurar que los detalles registrados correspondan únicamente a la iteración actual.
    """
    detalles_holguras.clear()

def reset_duracion():
    """
    Limpia los detalles del cálculo de la duración del proyecto.

    Garantiza que cada iteración del CPM extremo registre únicamente sus propias fórmulas y resultados.
    """

    detalles_duracion.clear()

def reset_coste():
    """
    Limpia los detalles del cálculo del coste total del proyecto.

    Se usa antes de cada iteración para evitar mezclar trazas de cálculos anteriores con los de la iteración actual.
    """

    detalles_coste.clear()