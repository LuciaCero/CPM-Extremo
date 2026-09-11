"""
Shared fixtures for the test suite.

The reference project used across the tests is the one shipped as
``inputs/ejemplo1.xlsx``:

    Activity  Predecessors  Dn  De   Cn    Ce   Slope
    A         -              6   4   600   800    100
    B         A              8   6   900  1300    200
    C         A              5   3   400   600    100
    D         B, C           7   5   700  1100    200

Indirect costs: 0 fixed, 150 EUR per day.
"""

import pandas as pd
import pytest


def construir_df_actividades(duraciones=None):
    """
    Build the activities DataFrame for the reference project.

    Mirrors exactly what ``input.leer_input`` produces, so the CPM modules can be
    tested without going through the Excel reader.

    Parameters
    ----------
    duraciones : dict, optional
        Overrides for the normal duration of specific activities, e.g.
        ``{"C": 8}`` to force two simultaneous critical paths.
    """

    dn = {"A": 6, "B": 8, "C": 5, "D": 7}
    if duraciones:
        dn.update(duraciones)

    df = pd.DataFrame(
        {
            "Actividad": ["A", "B", "C", "D"],
            "Predecesor": [[], ["A"], ["A"], ["B", "C"]],
            "Sucesor": [["B", "C"], ["D"], ["D"], []],
            "Dn": [dn["A"], dn["B"], dn["C"], dn["D"]],
            "De": [4, 6, 3, 5],
            "Cn": [600.0, 900.0, 400.0, 700.0],
            "Ce": [800.0, 1300.0, 600.0, 1100.0],
        }
    )

    return df[["Actividad", "Predecesor", "Sucesor", "Dn", "De", "Cn", "Ce"]]


@pytest.fixture
def df_actividades():
    """Activities of the reference project."""
    return construir_df_actividades()


@pytest.fixture
def df_proyecto():
    """Indirect costs of the reference project: 0 fixed, 150 EUR per day."""
    return pd.DataFrame([{"C_indirecto": 0.0, "C_indirecto_diario": 150.0}])


@pytest.fixture(autouse=True)
def estado_global_limpio():
    """
    Reset the module-level state before every test.

    ``cpm_extremo.shared`` keeps the symbolic traces and the set of
    non-reducible activities in module-level containers. Without this reset the
    outcome of one test would leak into the next one.
    """

    from cpm_extremo import shared

    shared.actividades_no_reducibles.clear()
    shared.reset_early()
    shared.reset_last()
    shared.reset_holguras()
    shared.reset_duracion()
    shared.reset_coste()

    yield

    shared.actividades_no_reducibles.clear()
