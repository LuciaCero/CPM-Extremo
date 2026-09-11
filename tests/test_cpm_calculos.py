"""Tests for the classic CPM calculations: early/last, float and critical paths."""

from cpm_extremo import grafo as G
from cpm_extremo.cpm import (
    camino_critico as critico,
    costes,
    duracion,
    early_last,
    estado,
    holguras,
)

from conftest import construir_df_actividades


def _preparar(df):
    """Build the graph and run one full CPM pass over it."""

    g = G.reducir_grafo(G.crear_grafo(df))
    df_early_last = early_last.calcular_early_last(g)
    df_holguras = holguras.calcular_tabla_holguras(g, df_early_last)
    return g, df_early_last, df_holguras


def test_el_proyecto_de_referencia_dura_21_dias(df_actividades):
    """A(6) + B(8) + D(7) = 21 days, the longest path."""

    g, _, df_holguras = _preparar(df_actividades)

    criticas = critico.obtener_actividades_criticas(df_holguras)
    caminos = critico.calcular_caminos_criticos(g, criticas)

    assert duracion.calcular_duracion_proyecto(df_holguras, caminos) == 21


def test_las_actividades_criticas_son_A_B_y_D(df_actividades):
    """C has float, so it is not on the critical path."""

    _, _, df_holguras = _preparar(df_actividades)

    criticas = critico.obtener_actividades_criticas(df_holguras)

    assert set(criticas) == {"A", "B", "D"}


def test_la_holgura_de_C_es_3(df_actividades):
    """C takes 5 days where B takes 8, so it can slip 3 days."""

    _, _, df_holguras = _preparar(df_actividades)

    holgura_c = df_holguras.loc[df_holguras["Actividad"] == "C", "Hij"].iloc[0]

    assert holgura_c == 3


def test_las_actividades_criticas_tienen_holgura_cero(df_actividades):
    """Being critical and having zero total float are the same thing."""

    _, _, df_holguras = _preparar(df_actividades)

    for _, fila in df_holguras.iterrows():
        assert fila["Critica"] == (fila["Hij"] == 0)


def test_early_del_nodo_inicial_es_cero(df_actividades):
    """The project starts at time zero."""

    g, df_early_last, _ = _preparar(df_actividades)

    nodo_inicial = next(n for n in g.nodes if g.in_degree(n) == 0)
    early = df_early_last.loc[df_early_last["Nodo"] == nodo_inicial, "Early"].iloc[0]

    assert early == 0


def test_early_y_last_coinciden_en_el_nodo_final(df_actividades):
    """The final event cannot be delayed, so its Early equals its Last."""

    g, df_early_last, _ = _preparar(df_actividades)

    nodo_final = next(n for n in g.nodes if g.out_degree(n) == 0)
    fila = df_early_last.loc[df_early_last["Nodo"] == nodo_final].iloc[0]

    assert fila["Early"] == fila["Last"] == 21


def test_hay_un_unico_camino_critico(df_actividades):
    """The reference project has exactly one critical path: A, B, D."""

    g, _, df_holguras = _preparar(df_actividades)

    criticas = critico.obtener_actividades_criticas(df_holguras)
    caminos = critico.calcular_caminos_criticos(g, criticas)

    assert caminos == [["A", "B", "D"]]


def test_dos_caminos_criticos_simultaneos():
    """With C = 8 days both branches take 21 days and both become critical."""

    df = construir_df_actividades({"C": 8})
    g, _, df_holguras = _preparar(df)

    criticas = critico.obtener_actividades_criticas(df_holguras)
    caminos = critico.calcular_caminos_criticos(g, criticas)

    assert set(criticas) == {"A", "B", "C", "D"}
    # The order in which the paths are returned is not guaranteed.
    assert {tuple(c) for c in caminos} == {("A", "B", "D"), ("A", "C", "D")}
    assert duracion.calcular_duracion_proyecto(df_holguras, caminos) == 21


def test_coste_directo_inicial(df_actividades):
    """600 + 900 + 400 + 700 = 2600 EUR at normal durations."""

    df_estado = estado.construir_estado_inicial(df_actividades)

    assert df_estado["Coste"].sum() == 2600.0


def test_coste_total_inicial(df_actividades, df_proyecto):
    """2600 direct + 150 * 21 indirect = 5750 EUR."""

    df_estado = estado.construir_estado_inicial(df_actividades)

    assert costes.calcular_coste_total(df_estado, df_proyecto, 21) == 5750.0


def test_el_estado_inicial_usa_duraciones_y_costes_normales(df_actividades):
    """Before any crashing every activity sits at its normal values."""

    df_estado = estado.construir_estado_inicial(df_actividades)

    assert list(df_estado["Duracion"]) == [6, 8, 5, 7]
    assert list(df_estado["Coste"]) == [600.0, 900.0, 400.0, 700.0]
