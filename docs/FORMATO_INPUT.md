# Formato del Excel de entrada

Este documento especifica la estructura exacta que debe tener el fichero `.xlsx` que recibe el programa. El lector ([`src/cpm_extremo/input/leer_excel.py`](../src/cpm_extremo/input/leer_excel.py)) accede a los datos **por posición de fila y columna**, no buscando etiquetas. Esto significa que:

> **Importante:** si desplazas una fila, el programa leerá datos incorrectos **sin avisar**. Para crear un input nuevo, duplica [`inputs/ejemplo1.xlsx`](../inputs/ejemplo1.xlsx) y sobrescribe los valores sin insertar ni eliminar filas.

---

## Vista general

El fichero se lee con `pandas.read_excel()`, que toma la **primera fila como cabecera**. Por eso, la numeración de filas que usa el código está desplazada una posición respecto a la que se ve en Excel.

| Fila en Excel | Índice en el código | Columna A | Columnas B en adelante |
|:---:|:---:|---|---|
| 1 | *(cabecera)* | `Duración` | Nombres de las actividades: `A`, `B`, `C`, ... |
| 2 | `0` | `normal` | Duración normal de cada actividad (`Dn`) |
| 3 | `1` | `extrema` | Duración extrema de cada actividad (`De`) |
| 4 | `2` | *(vacía)* | *(vacía)* |
| 5 | `3` | `Costes` | Nombres de las actividades (repetidos) |
| 6 | `4` | `normal` | Coste normal de cada actividad (`Cn`) |
| 7 | `5` | `extrema` | Coste extremo de cada actividad (`Ce`) |
| 8 | `6` | *(vacía)* | *(vacía)* |
| 9 | `7` | `Costes indirectos` | `A+`, `BX` (etiquetas del formato) |
| 10 | `8` | *(vacía)* | Coste fijo `A`, coste diario `B` |
| 11 | `9` | *(vacía)* | *(vacía)* |
| 12 | `10` | `Dependencias` | Nombres de las actividades (repetidos) |
| 13 en adelante | `11` en adelante | Nombre de actividad | Matriz de precedencias |

Las filas vacías son **obligatorias**: el código las cuenta al calcular los desplazamientos.

---

## Bloque 1 — Duraciones (filas 0 y 1)

```
           A    B    C    D
normal     6    8    5    7
extrema    4    6    3    5
```

| Campo | Significado |
|---|---|
| `Dn` (normal) | Duración de la actividad en condiciones habituales, en días. |
| `De` (extrema) | Duración mínima técnicamente alcanzable, en días, por mucho que se aceleren los recursos. |

**El número de actividades del proyecto se deduce de esta fila**, contando cuántos valores no vacíos hay en la fila `0`. Las columnas sobrantes de la plantilla (por ejemplo `E` a `O` en el ejemplo, que están vacías) se ignoran.

Restricción: `De <= Dn`. Si `De = Dn`, la actividad no admite reducción y recibirá pendiente infinita, lo que la excluye automáticamente de las candidatas a reducir.

---

## Bloque 2 — Costes (filas 4 y 5)

```
           A     B     C     D
normal    600   900   400   700
extrema   800  1300   600  1100
```

| Campo | Significado |
|---|---|
| `Cn` (normal) | Coste directo de ejecutar la actividad en su duración normal, en euros. |
| `Ce` (extrema) | Coste directo de ejecutarla en su duración extrema, en euros. |

Se convierten a `float`, así que admiten decimales usando **punto** como separador.

Normalmente `Ce > Cn`: acelerar una actividad cuesta más. A partir de estos cuatro valores el programa calcula la pendiente de coste:

```
pendiente = (Ce - Cn) / (Dn - De)
```

Es decir, cuántos euros de más cuesta cada día que se recorta la actividad. El algoritmo siempre recorta primero la actividad crítica con la pendiente más barata.

---

## Bloque 3 — Costes indirectos (fila 8)

```
                    (col. B)   (col. C)
Costes indirectos      A+         BX
                                 150
```

Los costes indirectos siguen el modelo lineal `A + B·X`, donde `X` es la duración total del proyecto:

| Columna | Campo interno | Significado |
|---|---|---|
| Primera (B en Excel) | `C_indirecto` | Coste fijo `A`: se paga una sola vez, sea cual sea la duración. |
| Segunda (C en Excel) | `C_indirecto_diario` | Coste diario `B`: se multiplica por los días que dure el proyecto. |

**Las celdas vacías se interpretan como 0.** En el ejemplo, el coste fijo está vacío y el diario es 150, de modo que el coste indirecto es `0 + 150 · duración`.

---

## Bloque 4 — Matriz de dependencias (fila 10 en adelante)

```
Dependencias   A    B    C    D
A                   1    1
B                             1
C                             1
D
```

La fila `10` es la cabecera. A partir de la fila `11` hay una fila por actividad, en el mismo orden que las columnas.

**Regla de lectura:** un `1` en la celda situada en la fila `X` y la columna `Y` significa que **`X` es predecesora de `Y`**, o dicho de otro modo, que `Y` no puede empezar hasta que `X` termine.

En el ejemplo anterior:

- `A` es predecesora de `B` y de `C`.
- `B` es predecesora de `D`.
- `C` es predecesora de `D`.
- `D` no es predecesora de nadie, así que es la actividad final.

Esto describe el proyecto: `A` arranca, se abre en dos ramas paralelas `B` y `C`, y ambas convergen en `D`.

### Detalles

- Las celdas sin relación se dejan **vacías**, no con un `0`.
- Los **sucesores se derivan automáticamente** invirtiendo esta matriz. No hay que declararlos por separado.
- Las actividades **sin ninguna predecesora** cuelgan del nodo inicial del grafo.
- Las actividades **sin ninguna sucesora** se conectan al nodo final mediante actividades ficticias.
- La matriz **no puede contener ciclos**. El programa lo valida antes de construir el grafo y, si detecta uno, aborta mostrando el ciclo encontrado:

  ```
  ERROR: Dependencias cíclicas detectadas: [('A', 'B', 'forward'), ('B', 'A', 'forward')]
  ```

---

## Ejemplo completo

Este es el contenido de `inputs/ejemplo1.xlsx`, un proyecto de cuatro actividades:

| | A | B | C | D |
|---|---|---|---|---|
| **Duración normal** | 6 | 8 | 5 | 7 |
| **Duración extrema** | 4 | 6 | 3 | 5 |
| **Coste normal** | 600 | 900 | 400 | 700 |
| **Coste extremo** | 800 | 1300 | 600 | 1100 |
| **Pendiente** | 100 | 200 | 100 | 200 |

Coste indirecto: `0 + 150 · duración`.

Dependencias: `A → {B, C}`, `B → D`, `C → D`.

---

## Lista de comprobación antes de ejecutar

- [ ] La fila 1 de Excel contiene los nombres de las actividades a partir de la columna B.
- [ ] Las filas de duraciones, costes, indirectos y dependencias están en sus posiciones exactas.
- [ ] Las filas separadoras vacías siguen presentes.
- [ ] `De <= Dn` para todas las actividades.
- [ ] Los decimales usan punto, no coma.
- [ ] La matriz de dependencias es cuadrada y cubre todas las actividades.
- [ ] Las dependencias no forman ciclos.
- [ ] Hay al menos una actividad sin predecesoras y al menos una sin sucesoras.
