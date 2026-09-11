import pandas as pd
from cpm_extremo import shared

def calcular_coste_total(estado, df_proyecto, duracion):
    """
    Calcula el coste total del proyecto para una duración dada.

    Suma el coste directo (dependiente de las actividades) y el coste indirecto (dependiente de la duración del proyecto). Además, registra los datos para añadirlos a la salida output_pert.txt.

    Parámetros
    ----------
    estado : pandas.DataFrame
        Estado actual de las actividades, incluyendo su coste directo.
    df_proyecto : pandas.DataFrame
        Parámetros globales del proyecto, incluyendo costes indirectos.
    duracion : float
        Duración total del proyecto en la iteración actual.

    Devuelve
    --------
    float
        Coste total del proyecto.
    """

    shared.reset_coste()

    cd = _calcular_coste_directo(estado)
    ci = _calcular_coste_indirecto(df_proyecto, duracion)

    total = cd + ci

    formula = (
        f"$C_{{\\text{{total}}}} = C_d + C_i = {cd} + {ci} = {total}$\\\\"
    )

    shared.detalles_coste.append(formula)

    return total

def _calcular_coste_directo(estado: pd.DataFrame) -> float:
    """
    Calcula el coste directo total del proyecto.

    Suma los costes individuales de cada actividad según el estado actual y registra la expresión simbólica y numérica utilizada en los detalles del cálculo para añadirlos a la salida output_pert.txt.

    Parámetros
    ----------
    estado : pandas.DataFrame
        Estado actual de las actividades, incluyendo su coste directo.

    Devuelve
    --------
    float
        Coste directo total.
    """
    
    actividades = estado["Actividad"].tolist()
    costes = estado["Coste"].tolist()

    simbolica = " + ".join(f"D_{{{act}}}" for act in actividades)

    numerica = " + ".join(str(c) for c in costes)

    total = sum(costes)

    formula = (
        f"$C_d = {simbolica} = {numerica} = {total}$\\\\"
    )

    shared.detalles_coste.append(formula)

    return total

def _calcular_coste_indirecto(df_proyecto: pd.DataFrame, duracion: float):
    """
    Calcula el coste indirecto del proyecto en función de su duración.

    Aplica la fórmula estándar: coste fijo inicial más el coste diario multiplicado por la duración del proyecto. Registra la fórmula simbólica y numérica utilizada para añadirlos a la salida output_pert.txt.

    Parámetros
    ----------
    df_proyecto : pandas.DataFrame
        Parámetros del proyecto con costes indirectos fijo y diario.
    duracion : float
        Duración total del proyecto.

    Devuelve
    --------
    float
        Coste indirecto total.
    """

    fila = df_proyecto.iloc[0]

    C0 = fila["C_indirecto"]
    Cd = fila["C_indirecto_diario"]

    total = C0 + duracion * Cd

    formula = (
        f"$C_i = C_0 + D_{{proyecto}} \\cdot C_d = {C0} + {duracion} \\cdot {Cd} = {total}$\\\\"
    )

    shared.detalles_coste.append(formula)

    return total