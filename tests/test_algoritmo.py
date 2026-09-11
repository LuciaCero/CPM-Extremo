"""End-to-end tests for the CPM crashing loop."""

from cpm_extremo import grafo as G
from cpm_extremo.cpm import algoritmo


def _ejecutar(df_actividades, df_proyecto):
    """Run the full crashing loop over the reference project."""

    g = G.reducir_grafo(G.crear_grafo(df_actividades))
    return algoritmo.algoritmo_cpm(g, df_actividades, df_proyecto)


def test_curva_coste_tiempo_completa(df_actividades, df_proyecto):
    """
    The cost-time curve of the reference project, computed by hand.

    Crashing is worth it while the cheapest available slope (100 EUR/day) stays
    below the indirect cost (150 EUR/day). Once only 200 EUR/day activities are
    left, the total cost starts climbing again.
    """

    _, historial_coste_tiempo, _ = _ejecutar(df_actividades, df_proyecto)

    assert historial_coste_tiempo == [
        (21, 5750.0),
        (20, 5700.0),
        (19, 5650.0),
        (18, 5700.0),
        (17, 5750.0),
    ]


def test_el_optimo_son_19_dias_y_5650_euros(df_actividades, df_proyecto):
    """The minimum total cost of the reference project."""

    historial, historial_coste_tiempo, idx_optima = _ejecutar(
        df_actividades, df_proyecto
    )

    assert historial_coste_tiempo[idx_optima] == (19, 5650.0)
    assert historial[idx_optima]["DuracionProyecto"] == 19
    assert historial[idx_optima]["CosteTotal"] == 5650.0


def test_la_primera_iteracion_es_el_proyecto_sin_reducir(df_actividades, df_proyecto):
    """Iteration 0 must match the plain CPM result."""

    historial, _, _ = _ejecutar(df_actividades, df_proyecto)
    inicial = historial[0]

    assert inicial["DuracionProyecto"] == 21
    assert inicial["CosteTotal"] == 5750.0
    assert set(inicial["ActividadesCriticas"]) == {"A", "B", "D"}


def test_el_algoritmo_para_tras_dos_subidas_consecutivas(df_actividades, df_proyecto):
    """
    Two extra iterations are recorded past the optimum, on purpose, so the
    cost-time curve shows its rising branch.
    """

    _, historial_coste_tiempo, idx_optima = _ejecutar(df_actividades, df_proyecto)

    assert idx_optima == len(historial_coste_tiempo) - 3

    costes = [c for _, c in historial_coste_tiempo]
    assert costes[idx_optima + 1] > costes[idx_optima]
    assert costes[idx_optima + 2] > costes[idx_optima + 1]


def test_la_duracion_decrece_de_forma_monotona(df_actividades, df_proyecto):
    """Each iteration crashes exactly one day off the project."""

    _, historial_coste_tiempo, _ = _ejecutar(df_actividades, df_proyecto)

    duraciones = [d for d, _ in historial_coste_tiempo]

    assert duraciones == sorted(duraciones, reverse=True)
    assert all(a - b == 1 for a, b in zip(duraciones, duraciones[1:]))


def test_ninguna_actividad_baja_de_su_duracion_extrema(df_actividades, df_proyecto):
    """The crash limit De must be respected in every recorded iteration."""

    historial, _, _ = _ejecutar(df_actividades, df_proyecto)
    minimos = dict(zip(df_actividades["Actividad"], df_actividades["De"]))

    for iteracion in historial:
        for _, fila in iteracion["Estado"].iterrows():
            assert fila["Duracion"] >= minimos[fila["Actividad"]]


def test_el_historial_registra_una_entrada_por_punto_de_la_curva(
    df_actividades, df_proyecto
):
    """Both histories must stay aligned, they are indexed by the same position."""

    historial, historial_coste_tiempo, _ = _ejecutar(df_actividades, df_proyecto)

    assert len(historial) == len(historial_coste_tiempo)

    for iteracion, (dur, coste) in zip(historial, historial_coste_tiempo):
        assert iteracion["DuracionProyecto"] == dur
        assert iteracion["CosteTotal"] == coste
