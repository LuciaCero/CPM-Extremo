"""Tests for the cost slope calculation."""

import numpy as np
import pandas as pd

from cpm_extremo.cpm import pendientes


def test_pendientes_del_proyecto_de_referencia(df_actividades):
    """Slope = (Ce - Cn) / (Dn - De) for every activity."""

    resultado = pendientes.calcular_pendientes(df_actividades)
    obtenidas = dict(zip(resultado["Actividad"], resultado["Pendiente"]))

    assert obtenidas == {"A": 100.0, "B": 200.0, "C": 100.0, "D": 200.0}


def test_actividad_no_reducible_tiene_pendiente_infinita():
    """An activity with Dn = De cannot be crashed, so its slope is infinite."""

    df = pd.DataFrame(
        {
            "Actividad": ["X"],
            "Dn": [5],
            "De": [5],
            "Cn": [100.0],
            "Ce": [100.0],
        }
    )

    resultado = pendientes.calcular_pendientes(df)

    assert resultado["Pendiente"].iloc[0] == np.inf


def test_la_pendiente_no_depende_del_orden_de_las_filas(df_actividades):
    """Reordering the DataFrame must not change any slope."""

    invertido = df_actividades.iloc[::-1].reset_index(drop=True)

    normal = pendientes.calcular_pendientes(df_actividades)
    revertido = pendientes.calcular_pendientes(invertido)

    assert dict(zip(normal["Actividad"], normal["Pendiente"])) == dict(
        zip(revertido["Actividad"], revertido["Pendiente"])
    )
