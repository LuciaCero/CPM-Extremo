# The CPM crashing algorithm

Reference document on the mathematical basis of the implemented method and how it maps onto the code in this repository.

- [1. The problem](#1-the-problem)
- [2. The AOA graph](#2-the-aoa-graph)
- [3. Classic CPM](#3-classic-cpm)
- [4. Cost-time analysis](#4-cost-time-analysis)
- [5. The crashing loop](#5-the-crashing-loop)
- [6. Traceability of the calculations](#6-traceability-of-the-calculations)
- [7. Code map](#7-code-map)

---

## 1. The problem

A project is made up of activities with durations and precedence relations. **Classic CPM** answers one question: how long does the project take, and which activities cannot slip?

**CPM crashing** answers a different one: if an activity can be sped up by paying more for it, how far is it worth doing so?

The tension is this:

- Speeding activities up **raises the direct cost**, because you pay for overtime, extra staff or better equipment.
- Shortening the project **lowers the indirect cost**, because you pay for fewer days of overhead, rent, supervision or late penalties.

Total cost is the sum of both, so it traces a U-shaped curve. The algorithm's job is to find its minimum.

---

## 2. The AOA graph

The project is modelled as an **Activity-on-Arrow** directed graph: each activity is an *edge*, and each node is an *event*, the instant at which every activity entering it has finished and every activity leaving it may start.

### Construction

`grafo/constructor.py` walks the activity table in two passes:

1. **Activities with no predecessors.** They hang directly off start node `1`.
2. **Activities with predecessors.** Two cases:
   - If all their predecessors end at the same node, the activity starts from that node.
   - If they end at different nodes, a **merge node** has to be created and wired from each predecessor node through **dummy activities** of duration 0.

Finally, every activity with no successors is connected to the end node through dummies, guaranteeing the graph has a single termination point.

### Why dummy activities are needed

The AOA representation has a limitation: an edge can only run from one node to another. If two activities share some but not all of their predecessors — say `C` depends on `A` and `B`, while `D` depends only on `A` — there is no way to draw it without introducing zero-duration helper edges that express the precedence without consuming time.

They are drawn as dashed grey lines and named `F_1`, `F_2`, and so on.

### Simplification

The initial construction produces more dummies and nodes than necessary. `grafo/reducir.py` cleans the graph up in several passes:

1. **Merging equivalent nodes.** Nodes whose incoming edges are all dummies coming from exactly the same set of predecessors are collapsed into one.
2. **Iterative dummy removal.** A node whose incoming edges are all dummies and that has at most one outgoing edge can be absorbed into its predecessors. This repeats until no further merges are possible.
3. **Reindexing.** Nodes are renumbered `1` to `n` in order, and the surviving dummies are renamed `F_1`, `F_2`, ... in a stable, reproducible way.

The merge condition (`_puede_unir`) rejects the operation if the two nodes share any predecessor or if the absorbed node has more than one outgoing edge, because in those cases merging would alter the project's precedence relations.

> **Note:** the AOA graph of a project is **not unique**. Another valid construction may use a different number of dummies and a different node numbering. The CPM results (early, last, float, duration, critical paths) are the same, but the node numbering may not match a solution worked out by hand.

---

## 3. Classic CPM

### Early: the forward pass

The **early** value of a node is the soonest that event can be reached. It is computed by walking the nodes in **topological order** from the start:

```
E_1 = 0                                    (start node)

E_j = Max { E_i + D_ij }  for every activity (i,j) entering j
```

The reasoning: event `j` happens once **all** activities reaching it have finished, so you wait for the latest one. Hence the maximum.

The **early value of the end node is the project duration**.

### Last: the backward pass

The **last** value of a node is the latest that event can be reached without delaying the project. It is computed in **reverse** topological order, starting from the end:

```
L_end = E_end                              (the project does not slip)

L_i = Min { L_j - D_ij }  for every activity (i,j) leaving i
```

The reasoning: if several activities leave `i`, you have to satisfy the most demanding one, the one that needs to start earliest. Hence the minimum.

### Float

The **total float** of an activity is how much it can slip without affecting the project duration:

```
H_ij = L_j - E_i - D_ij
```

That is: the time available between the earliest it can start and the latest it must finish, minus how long it actually takes.

An activity with **zero float is critical**: any delay on it propagates straight to the project finish date.

### Critical paths

A **critical path** is a chain of critical activities running from the start node to the end node. Its length equals the project duration.

`camino_critico.py` works it out by building a subgraph containing only the critical activities plus the dummies connecting critical nodes to each other, then enumerating every simple path from start to end. When translating each path from nodes to activities, dummies are dropped, since they represent no real work.

**There can be more than one critical path at a time.** The algorithm returns all of them, and that matters: if two parallel critical paths exist, shortening an activity on just one of them does not reduce the project duration, because the other path still dictates the length.

---

## 4. Cost-time analysis

### The cost slope

For each activity the program works out what buying one day costs:

```
slope = (Ce - Cn) / (Dn - De)
```

If `Dn = De` the activity cannot be shortened, and it is assigned an **infinite** slope so it drops out without needing a special case.

The model assumes cost grows **linearly** between the normal and crash points. That is a standard simplification in the CPM literature: in practice the cost of speeding up tends to be convex, but the linear approximation keeps the problem solvable by hand.

### Total cost

```
total cost = direct cost + indirect cost

direct cost   = sum of the current costs of every activity
indirect cost = fixed cost + project duration * daily cost
```

The direct cost **rises** with every crash, by exactly the slope of the crashed activity. The indirect cost **falls** by the daily rate for every day cut off the project.

Hence the intuitive rule: **crashing is worth it while the activity's slope is lower than the daily indirect cost.** Once the cheapest available slope exceeds the daily rate, speeding up further becomes expensive and the curve starts climbing.

---

## 5. The crashing loop

### Pseudocode

```
INPUT: activity table, indirect cost parameters

graph  <- simplify(build_AOA_graph(activities))
state  <- {every activity at its Dn duration and Cn cost}
slopes <- compute_slopes(activities)

previous_cost   <- infinity
consecutive_rises <- 0
history           <- []

REPEAT:

    # --- Full CPM recomputation over the current state ---
    early_last  <- compute_early_last(graph)
    float       <- compute_float(graph, early_last)
    critical    <- activities with float = 0
    paths       <- critical_paths(graph, critical)
    duration    <- max(length of each critical path)
    total_cost  <- direct_cost(state) + indirect_cost(duration)

    record (duration, total_cost) in history

    # --- Stopping criterion 1 ---
    IF total_cost > previous_cost:
        consecutive_rises <- consecutive_rises + 1
    ELSE:
        consecutive_rises <- 0

    IF consecutive_rises >= 2:
        STOP

    previous_cost <- total_cost

    # --- Selection ---
    activity <- crashable critical activity with the LOWEST slope

    # --- Stopping criterion 2 ---
    IF there is none:
        STOP

    # --- Crash ---
    state <- crash_one_day(activity, state)
    propagate_durations(graph, state)

OUTPUT: full history + index of the minimum-cost iteration
```

### Choosing which activity to crash

Among the critical activities, those already at their crash duration and those previously flagged as non-crashable are discarded. Of the rest, the one with the **lowest slope** is picked: the cheapest day available.

On a tie, the first one in DataFrame order wins. Arbitrary, but deterministic, so two runs on the same input give the same result.

### Crashing and validating it

`reduccion_actividades.py` does not apply the crash blindly. It works on **copies** of the state and the graph, recomputes the full CPM, and only then decides whether the change is admissible. It is reverted if:

- The new duration would fall below the activity's crash duration.
- The crash changes neither the project duration nor the cost, meaning it achieves nothing.

When reverted, the activity is added to the **non-crashable** set and is never considered again in later iterations. That keeps the loop from getting stuck endlessly retrying the same useless activity.

This case typically shows up with several parallel critical paths: crashing an activity on one of them does not shorten the project, because another path holds the duration.

### Why the algorithm keeps going past the optimum

The stopping condition is not "cost went up once" but **twice in a row**. The reason is presentational: stopping at the exact minimum would leave the cost-time curve with no rising branch, and it would not visually read as a minimum. The two extra iterations draw that rise.

That is why the optimum is not the last iteration of the history but the cheapest one, which the algorithm locates and returns as `idx_optima`.

---

## 6. Traceability of the calculations

One design particularity: on top of returning their result, every calculation **records the symbolic and numeric working** that produced it.

The `shared/globales.py` module keeps lists of details that each calculation module fills in and that are cleared at the start of every iteration. What gets stored are preformatted LaTeX fragments:

```latex
$E_4 = Max \{E_2 + B, E_3 + C\} = Max \{6 + 8, 6 + 5\} = Max \{14, 11\} = 14$
$H_B = H_{2,4} = L_4 - E_2 - D_{B} = 14 - 6 - 8 = 0$
$C_d = D_{A} + D_{B} + D_{C} + D_{D} = 600 + 900 + 400 + 700 = 2600$
```

The report generator collects these traces as each iteration closes and embeds them in the document. The upshot is that the report does not present bare final numbers, but the same working you would write solving the exercise by hand, which makes every step checkable.

---

## 7. Code map

How the concepts in this document map onto the files implementing them:

| Concept | Module | Main function |
|---|---|---|
| Reading the spreadsheet | `input/leer_excel.py` | `leer_input()` |
| Building the AOA graph | `grafo/constructor.py` | `crear_grafo()` |
| Cycle validation | `grafo/constructor.py` | `_validar_dependencias()` |
| Graph simplification | `grafo/reducir.py` | `reducir_grafo()` |
| Propagating durations | `grafo/actualizar.py` | `actualizar_duraciones()` |
| Initial state | `cpm/estado.py` | `construir_estado_inicial()` |
| Cost slopes | `cpm/pendientes.py` | `calcular_pendientes()` |
| Early and last | `cpm/early_last.py` | `calcular_early_last()` |
| Float and criticality | `cpm/holguras.py` | `calcular_tabla_holguras()` |
| Critical paths | `cpm/camino_critico.py` | `calcular_caminos_criticos()` |
| Choosing the activity to crash | `cpm/camino_critico.py` | `obtener_actividades_criticas_reducibles()` |
| Project duration | `cpm/duracion.py` | `calcular_duracion_proyecto()` |
| Direct and indirect cost | `cpm/costes.py` | `calcular_coste_total()` |
| Validated crashing | `cpm/reduccion_actividades.py` | `reducir_duracion()` |
| Main loop | `cpm/algoritmo.py` | `algoritmo_cpm()` |
| Symbolic traces | `shared/globales.py` | the `detalles_*` lists |
| LaTeX report | `output/latex_informe.py` | `generar_pert()` |

---

## References

- Kelley, J. E. and Walker, M. R. (1959). *Critical-Path Planning and Scheduling*. Proceedings of the Eastern Joint Computer Conference. The original paper on the method.
- Hillier, F. S. and Lieberman, G. J. *Introduction to Operations Research*. Chapter on PERT/CPM and cost-time analysis.
- [NetworkX documentation](https://networkx.org/documentation/stable/), for the directed graph operations and topological ordering.
