# El algoritmo CPM extremo

Documento de referencia sobre el fundamento matemático del método implementado y sobre cómo se traduce en el código de este repositorio.

- [1. El problema](#1-el-problema)
- [2. El grafo AOA](#2-el-grafo-aoa)
- [3. CPM clásico](#3-cpm-clásico)
- [4. Análisis coste-tiempo](#4-análisis-coste-tiempo)
- [5. El bucle del CPM extremo](#5-el-bucle-del-cpm-extremo)
- [6. Trazabilidad de los cálculos](#6-trazabilidad-de-los-cálculos)
- [7. Mapa de código](#7-mapa-de-código)

---

## 1. El problema

Un proyecto se compone de actividades con duraciones y relaciones de precedencia. El **CPM clásico** responde a una pregunta: ¿cuánto dura el proyecto y qué actividades no admiten retraso?

El **CPM extremo**, o *crashing*, responde a otra distinta: si se puede acelerar una actividad pagando más por ella, ¿hasta qué punto compensa hacerlo?

La tensión es la siguiente:

- Acelerar actividades **sube el coste directo**, porque hay que pagar horas extra, más personal o mejores medios.
- Acortar el proyecto **baja el coste indirecto**, porque se pagan menos días de estructura, alquileres, supervisión o penalizaciones por retraso.

El coste total es la suma de ambos, así que describe una curva en forma de U. El objetivo del algoritmo es encontrar su mínimo.

---

## 2. El grafo AOA

El proyecto se representa como un grafo dirigido **Activity-on-Arrow**: cada actividad es una *arista*, y cada nodo es un *suceso*, el instante en que terminan todas las actividades que entran en él y pueden empezar todas las que salen.

### Construcción

`grafo/constructor.py` recorre la tabla de actividades en dos pasadas:

1. **Actividades sin predecesoras.** Cuelgan directamente del nodo inicial `1`.
2. **Actividades con predecesoras.** Se distinguen dos casos:
   - Si todas sus predecesoras terminan en el mismo nodo, la actividad arranca de ese nodo.
   - Si terminan en nodos distintos, hay que crear un **nodo de convergencia** y conectarlo desde cada nodo predecesor mediante **actividades ficticias** de duración 0.

Por último, todas las actividades sin sucesoras se conectan al nodo final mediante ficticias, garantizando que el grafo tenga un único punto de terminación.

### Por qué hacen falta las actividades ficticias

La representación AOA tiene una limitación: una arista solo puede ir de un nodo a otro. Si dos actividades comparten parcialmente sus predecesoras (por ejemplo, `C` depende de `A` y `B`, pero `D` depende solo de `A`), no hay forma de dibujarlo sin introducir aristas auxiliares de duración cero que expresen la precedencia sin consumir tiempo.

Se dibujan con trazo discontinuo gris y se nombran `F_1`, `F_2`, etc.

### Simplificación

La construcción inicial genera más ficticias y nodos de los necesarios. `grafo/reducir.py` limpia el grafo en varias pasadas:

1. **Unificación de nodos equivalentes.** Nodos cuyas entradas son todas ficticias y proceden exactamente del mismo conjunto de predecesores se fusionan en uno solo.
2. **Eliminación iterativa de ficticias.** Un nodo cuyas entradas son todas ficticias y que tiene como mucho una salida puede absorberse en sus predecesores. El proceso se repite hasta que no quedan fusiones posibles.
3. **Reindexado.** Los nodos se renumeran de `1` a `n` en orden, y las ficticias supervivientes se renombran `F_1`, `F_2`, ... de forma estable y reproducible.

La condición de fusión (`_puede_unir`) rechaza el merge si los dos nodos comparten algún predecesor o si el nodo absorbido tiene más de una salida, porque en esos casos la fusión alteraría las relaciones de precedencia del proyecto.

> **Nota:** el grafo AOA de un proyecto **no es único**. Otra construcción válida puede tener distinto número de ficticias y distinta numeración de nodos. Los resultados del CPM (Early, Last, holguras, duración, caminos críticos) son los mismos, pero la numeración de nodos puede no coincidir con la de una solución hecha a mano.

---

## 3. CPM clásico

### Early: el recorrido hacia delante

El **Early** de un nodo es el instante más temprano en que puede alcanzarse ese suceso. Se calcula recorriendo los nodos en **orden topológico** desde el inicio:

```
E_1 = 0                                    (nodo inicial)

E_j = Max { E_i + D_ij }  para toda actividad (i,j) que entra en j
```

La lógica: el suceso `j` ocurre cuando han terminado **todas** las actividades que llegan a él, así que hay que esperar a la más tardía. De ahí el máximo.

El **Early del nodo final es la duración del proyecto**.

### Last: el recorrido hacia atrás

El **Last** de un nodo es el instante más tardío en que puede alcanzarse ese suceso sin retrasar el proyecto. Se calcula en orden topológico **inverso**, partiendo del final:

```
L_final = E_final                          (el proyecto no se retrasa)

L_i = Min { L_j - D_ij }  para toda actividad (i,j) que sale de i
```

La lógica: si desde `i` salen varias actividades, hay que respetar la más exigente, la que necesita empezar antes. De ahí el mínimo.

### Holguras

La **holgura total** de una actividad es el margen de retraso que admite sin afectar a la duración del proyecto:

```
H_ij = L_j - E_i - D_ij
```

Es decir: el tiempo disponible entre el instante más temprano en que puede empezar y el más tardío en que debe acabar, menos lo que realmente tarda.

Una actividad con **holgura cero es crítica**: cualquier retraso suyo se propaga directamente a la fecha de fin del proyecto.

### Caminos críticos

Un **camino crítico** es una secuencia de actividades críticas que va del nodo inicial al final. Su duración coincide con la del proyecto.

`camino_critico.py` lo resuelve construyendo un subgrafo que contiene solo las actividades críticas más las ficticias que conectan nodos críticos entre sí, y enumerando después todos los caminos simples del inicio al final. Al traducir cada camino de nodos a actividades, las ficticias se descartan, porque no representan trabajo real.

**Puede haber más de un camino crítico simultáneo.** El algoritmo los devuelve todos, y esto importa: si existen dos caminos críticos paralelos, acortar una actividad de uno solo no reduce la duración del proyecto, porque el otro camino sigue imponiendo su longitud.

---

## 4. Análisis coste-tiempo

### La pendiente de coste

Para cada actividad se calcula cuánto cuesta ganar un día:

```
pendiente = (Ce - Cn) / (Dn - De)
```

Si `Dn = De`, la actividad no se puede acortar, y se le asigna pendiente **infinita** para excluirla sin necesidad de un caso especial.

El modelo asume que el coste crece **linealmente** entre el punto normal y el extremo. Es una simplificación habitual en la literatura de CPM: en la práctica el coste de acelerar suele ser convexo, pero la aproximación lineal mantiene el problema resoluble a mano.

### El coste total

```
C_total = C_directo + C_indirecto

C_directo   = suma de los costes actuales de todas las actividades
C_indirecto = C_fijo + duración_del_proyecto * C_diario
```

El coste directo **sube** con cada reducción, en exactamente el valor de la pendiente de la actividad reducida. El coste indirecto **baja** en `C_diario` por cada día que se acorta el proyecto.

De ahí la regla intuitiva: **merece la pena reducir mientras la pendiente de la actividad sea menor que el coste indirecto diario.** Cuando la pendiente más barata disponible supera al coste diario, seguir acelerando sale caro y la curva empieza a subir.

---

## 5. El bucle del CPM extremo

### Pseudocódigo

```
ENTRADA: tabla de actividades, parámetros de coste indirecto

grafo  <- simplificar(construir_grafo_AOA(actividades))
estado <- {cada actividad a su duración Dn y coste Cn}
pendientes <- calcular_pendientes(actividades)

coste_anterior      <- infinito
subidas_consecutivas <- 0
historial           <- []

REPETIR:

    # --- Recálculo completo del CPM sobre el estado actual ---
    early_last  <- calcular_early_last(grafo)
    holguras    <- calcular_holguras(grafo, early_last)
    criticas    <- actividades con holgura = 0
    caminos     <- caminos_criticos(grafo, criticas)
    duracion    <- max(longitud de cada camino crítico)
    coste_total <- coste_directo(estado) + coste_indirecto(duracion)

    registrar (duracion, coste_total) en historial

    # --- Criterio de parada 1 ---
    SI coste_total > coste_anterior:
        subidas_consecutivas <- subidas_consecutivas + 1
    SI NO:
        subidas_consecutivas <- 0

    SI subidas_consecutivas >= 2:
        PARAR

    coste_anterior <- coste_total

    # --- Selección ---
    actividad <- crítica reducible con MENOR pendiente

    # --- Criterio de parada 2 ---
    SI no hay ninguna:
        PARAR

    # --- Reducción ---
    estado <- reducir_un_dia(actividad, estado)
    propagar_duraciones(grafo, estado)

SALIDA: historial completo + índice de la iteración de coste mínimo
```

### La selección de la actividad a reducir

De entre las actividades críticas, se descartan las que ya están a su duración extrema y las marcadas previamente como no reducibles. De las que quedan, se elige la de **pendiente mínima**: el día más barato disponible.

Si hay empate, se toma la primera en el orden del DataFrame. Es arbitrario, pero determinista, de modo que dos ejecuciones sobre el mismo input dan el mismo resultado.

### La reducción y su validación

`reduccion_actividades.py` no aplica la reducción a ciegas. Trabaja sobre **copias** del estado y del grafo, recalcula el CPM completo, y solo entonces decide si el cambio es admisible. Se revierte si:

- La nueva duración caería por debajo de la duración extrema de la actividad.
- La reducción no cambia la duración del proyecto y tampoco altera el coste, es decir, no aporta nada.

Cuando se revierte, la actividad se añade al conjunto de **no reducibles** y no se vuelve a considerar en iteraciones posteriores. Así el bucle no se queda atascado reintentando indefinidamente la misma actividad inútil.

Este caso se da típicamente cuando hay varios caminos críticos en paralelo: reducir una actividad de uno de ellos no acorta el proyecto, porque otro camino mantiene la duración.

### Por qué el algoritmo sigue después del óptimo

La condición de parada no es "el coste ha subido una vez", sino **dos veces consecutivas**. La razón es la representación gráfica: parar en el mínimo exacto dejaría una curva coste-tiempo sin rama ascendente, y visualmente no se apreciaría que se trata de un mínimo. Las dos iteraciones extra dibujan esa subida.

Por eso el óptimo no es la última iteración del historial, sino la de coste mínimo, que el algoritmo localiza y devuelve como `idx_optima`.

---

## 6. Trazabilidad de los cálculos

Una particularidad del diseño: todos los cálculos, además de devolver su resultado, **registran el desarrollo simbólico y numérico** que los produjo.

El módulo `shared/globales.py` mantiene listas de detalles que cada módulo de cálculo va rellenando y que se vacían al inicio de cada iteración. Lo que se almacena son fragmentos LaTeX ya formateados:

```latex
$E_4 = Max \{E_2 + B, E_3 + C\} = Max \{6 + 8, 6 + 5\} = Max \{14, 11\} = 14$
$H_B = H_{2,4} = L_4 - E_2 - D_{B} = 14 - 6 - 8 = 0$
$C_d = D_{A} + D_{B} + D_{C} + D_{D} = 600 + 900 + 400 + 700 = 2600$
```

El generador de informes recoge estas trazas al cerrar cada iteración y las incrusta en el documento. El resultado es que el informe no presenta solo los números finales, sino el mismo desarrollo que se escribiría resolviendo el ejercicio a mano, lo que permite comprobar cada paso.

---

## 7. Mapa de código

Correspondencia entre los conceptos de este documento y los ficheros que los implementan:

| Concepto | Módulo | Función principal |
|---|---|---|
| Lectura del Excel | `input/leer_excel.py` | `leer_input()` |
| Construcción del grafo AOA | `grafo/constructor.py` | `crear_grafo()` |
| Validación de ciclos | `grafo/constructor.py` | `_validar_dependencias()` |
| Simplificación del grafo | `grafo/reducir.py` | `reducir_grafo()` |
| Propagación de duraciones | `grafo/actualizar.py` | `actualizar_duraciones()` |
| Estado inicial | `cpm/estado.py` | `construir_estado_inicial()` |
| Pendientes de coste | `cpm/pendientes.py` | `calcular_pendientes()` |
| Early y Last | `cpm/early_last.py` | `calcular_early_last()` |
| Holguras y criticidad | `cpm/holguras.py` | `calcular_tabla_holguras()` |
| Caminos críticos | `cpm/camino_critico.py` | `calcular_caminos_criticos()` |
| Selección de la actividad a reducir | `cpm/camino_critico.py` | `obtener_actividades_criticas_reducibles()` |
| Duración del proyecto | `cpm/duracion.py` | `calcular_duracion_proyecto()` |
| Coste directo e indirecto | `cpm/costes.py` | `calcular_coste_total()` |
| Reducción con validación | `cpm/reduccion_actividades.py` | `reducir_duracion()` |
| Bucle principal | `cpm/algoritmo.py` | `algoritmo_cpm()` |
| Trazas simbólicas | `shared/globales.py` | listas `detalles_*` |
| Informe LaTeX | `output/latex_informe.py` | `generar_pert()` |

---

## Referencias

- Kelley, J. E. y Walker, M. R. (1959). *Critical-Path Planning and Scheduling*. Proceedings of the Eastern Joint Computer Conference. Artículo original del método.
- Hillier, F. S. y Lieberman, G. J. *Introduction to Operations Research*. Capítulo sobre PERT/CPM y análisis coste-tiempo.
- [Documentación de NetworkX](https://networkx.org/documentation/stable/), para las operaciones sobre grafos dirigidos y el orden topológico.
