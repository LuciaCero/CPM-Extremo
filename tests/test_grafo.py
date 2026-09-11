"""Tests for building and simplifying the AOA graph."""

import networkx as nx
import pandas as pd
import pytest

from cpm_extremo import grafo as G
from cpm_extremo.grafo import constructor

from conftest import construir_df_actividades


def test_el_grafo_es_aciclico_y_tiene_un_unico_inicio_y_fin(df_actividades):
    """A well-formed AOA graph has exactly one source and one sink."""

    g = G.reducir_grafo(G.crear_grafo(df_actividades))

    assert nx.is_directed_acyclic_graph(g)
    assert len([n for n in g.nodes if g.in_degree(n) == 0]) == 1
    assert len([n for n in g.nodes if g.out_degree(n) == 0]) == 1


def test_todas_las_actividades_reales_estan_en_el_grafo(df_actividades):
    """Every activity of the project must appear as an edge."""

    g = G.reducir_grafo(G.crear_grafo(df_actividades))

    reales = {
        data["actividad"]
        for _, _, data in g.edges(data=True)
        if not data.get("ficticia", False)
    }

    assert reales == {"A", "B", "C", "D"}


def test_las_duraciones_llegan_al_grafo(df_actividades):
    """Edge durations must match the normal durations of the activities."""

    g = G.reducir_grafo(G.crear_grafo(df_actividades))

    duraciones = {
        data["actividad"]: data["duracion"]
        for _, _, data in g.edges(data=True)
        if not data.get("ficticia", False)
    }

    assert duraciones == {"A": 6, "B": 8, "C": 5, "D": 7}


def test_las_dependencias_ciclicas_se_rechazan():
    """A cycle in the precedence matrix must abort the run."""

    df = pd.DataFrame(
        {
            "Actividad": ["A", "B"],
            "Predecesor": [["B"], ["A"]],
            "Sucesor": [["B"], ["A"]],
            "Dn": [3, 4],
            "De": [2, 3],
            "Cn": [100.0, 200.0],
            "Ce": [150.0, 250.0],
        }
    )

    with pytest.raises(ValueError, match="[Cc]íclicas"):
        constructor._validar_dependencias(df)


def test_un_ciclo_termina_el_programa():
    """``crear_grafo`` turns the validation error into a clean exit."""

    df = pd.DataFrame(
        {
            "Actividad": ["A", "B"],
            "Predecesor": [["B"], ["A"]],
            "Sucesor": [["B"], ["A"]],
            "Dn": [3, 4],
            "De": [2, 3],
            "Cn": [100.0, 200.0],
            "Ce": [150.0, 250.0],
        }
    )

    with pytest.raises(SystemExit):
        G.crear_grafo(df)


def test_actualizar_duraciones_solo_toca_las_actividades_reales(df_actividades):
    """Dummy activities must keep duration 0 when the state is propagated."""

    g = G.reducir_grafo(G.crear_grafo(df_actividades))

    estado = pd.DataFrame(
        {"Actividad": ["A", "B", "C", "D"], "Duracion": [4, 6, 3, 5]}
    )
    G.actualizar_duraciones(g, estado)

    for _, _, data in g.edges(data=True):
        if data.get("ficticia", False):
            assert data["duracion"] == 0
        else:
            assert data["duracion"] == {"A": 4, "B": 6, "C": 3, "D": 5}[
                data["actividad"]
            ]


def test_la_numeracion_de_las_ficticias_es_consecutiva():
    """After simplification dummies are renamed F_1, F_2, ... without gaps."""

    df = construir_df_actividades()
    g = G.reducir_grafo(G.crear_grafo(df))

    ficticias = sorted(
        data["actividad"]
        for _, _, data in g.edges(data=True)
        if data.get("ficticia", False)
    )

    esperadas = [f"F_{i}" for i in range(1, len(ficticias) + 1)]
    assert ficticias == esperadas
