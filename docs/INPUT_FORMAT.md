# Input spreadsheet format

This document specifies the exact structure the `.xlsx` file handed to the program must have. The reader ([`src/cpm_extremo/input/leer_excel.py`](../src/cpm_extremo/input/leer_excel.py)) locates data **by row and column position**, not by looking up labels. Which means:

> **Important:** if you shift a row, the program will read the wrong data **without warning you**. To create a new input, duplicate [`inputs/ejemplo1.xlsx`](../inputs/ejemplo1.xlsx) and overwrite the values without inserting or deleting rows.

---

## Overview

The file is read with `pandas.read_excel()`, which treats the **first row as the header**. That is why the row numbering used by the code is offset by one from what you see in Excel.

| Excel row | Code index | Column A | Column B onwards |
|:---:|:---:|---|---|
| 1 | *(header)* | `Duración` | Activity names: `A`, `B`, `C`, ... |
| 2 | `0` | `normal` | Normal duration of each activity (`Dn`) |
| 3 | `1` | `extrema` | Crash duration of each activity (`De`) |
| 4 | `2` | *(empty)* | *(empty)* |
| 5 | `3` | `Costes` | Activity names again |
| 6 | `4` | `normal` | Normal cost of each activity (`Cn`) |
| 7 | `5` | `extrema` | Crash cost of each activity (`Ce`) |
| 8 | `6` | *(empty)* | *(empty)* |
| 9 | `7` | `Costes indirectos` | `A+`, `BX` (format labels) |
| 10 | `8` | *(empty)* | Fixed cost `A`, daily cost `B` |
| 11 | `9` | *(empty)* | *(empty)* |
| 12 | `10` | `Dependencias` | Activity names again |
| 13 onwards | `11` onwards | Activity name | Precedence matrix |

The empty rows are **mandatory**: the code counts them when computing offsets.

---

## Block 1 — Durations (rows 0 and 1)

```
           A    B    C    D
normal     6    8    5    7
extrema    4    6    3    5
```

| Field | Meaning |
|---|---|
| `Dn` (normal) | Duration of the activity under normal conditions, in days. |
| `De` (crash) | Shortest duration that is technically achievable, in days, no matter how many resources are thrown at it. |

**The number of activities in the project is derived from this row**, by counting how many non-empty values row `0` contains. Spare template columns (for example `E` through `O` in the sample file, which are empty) are ignored.

Constraint: `De <= Dn`. If `De = Dn` the activity cannot be crashed and gets an infinite slope, which automatically excludes it from the crashing candidates.

---

## Block 2 — Costs (rows 4 and 5)

```
           A     B     C     D
normal    600   900   400   700
extrema   800  1300   600  1100
```

| Field | Meaning |
|---|---|
| `Cn` (normal) | Direct cost of running the activity at its normal duration, in euros. |
| `Ce` (crash) | Direct cost of running it at its crash duration, in euros. |

They are cast to `float`, so decimals are allowed using a **dot** as the separator.

`Ce > Cn` in the usual case: speeding an activity up costs more. From these four values the program computes the cost slope:

```
slope = (Ce - Cn) / (Dn - De)
```

That is, how many extra euros each day shaved off the activity costs. The algorithm always crashes the critical activity with the cheapest slope first.

---

## Block 3 — Indirect costs (row 8)

```
                    (col. B)   (col. C)
Costes indirectos      A+         BX
                                 150
```

Indirect costs follow the linear model `A + B·X`, where `X` is the total duration of the project:

| Column | Internal field | Meaning |
|---|---|---|
| First (B in Excel) | `C_indirecto` | Fixed cost `A`, paid once regardless of duration. |
| Second (C in Excel) | `C_indirecto_diario` | Daily cost `B`, multiplied by the number of days the project runs. |

**Empty cells are read as 0.** In the sample file the fixed cost is empty and the daily cost is 150, so the indirect cost is `0 + 150 · duration`.

---

## Block 4 — Dependency matrix (row 10 onwards)

```
Dependencias   A    B    C    D
A                   1    1
B                             1
C                             1
D
```

Row `10` is the header. From row `11` on there is one row per activity, in the same order as the columns.

**How to read it:** a `1` in the cell at row `X`, column `Y` means that **`X` precedes `Y`**, or in other words, that `Y` cannot start until `X` is finished.

In the example above:

- `A` precedes `B` and `C`.
- `B` precedes `D`.
- `C` precedes `D`.
- `D` precedes nothing, so it is the final activity.

That describes the project: `A` kicks things off, splits into two parallel branches `B` and `C`, and both converge into `D`.

### Details

- Cells with no relation are left **empty**, not set to `0`.
- **Successors are derived automatically** by inverting this matrix. There is no need to declare them separately.
- Activities with **no predecessors** hang off the start node of the graph.
- Activities with **no successors** are wired to the end node through dummy activities.
- The matrix **cannot contain cycles**. The program validates this before building the graph and, if it finds one, aborts showing the cycle:

  ```
  ERROR: Dependencias cíclicas detectadas: [('A', 'B', 'forward'), ('B', 'A', 'forward')]
  ```

---

## Full example

This is the content of `inputs/ejemplo1.xlsx`, a four-activity project:

| | A | B | C | D |
|---|---|---|---|---|
| **Normal duration** | 6 | 8 | 5 | 7 |
| **Crash duration** | 4 | 6 | 3 | 5 |
| **Normal cost** | 600 | 900 | 400 | 700 |
| **Crash cost** | 800 | 1300 | 600 | 1100 |
| **Slope** | 100 | 200 | 100 | 200 |

Indirect cost: `0 + 150 · duration`.

Dependencies: `A → {B, C}`, `B → D`, `C → D`.

---

## Checklist before running

- [ ] Row 1 of the spreadsheet holds the activity names, starting at column B.
- [ ] The duration, cost, indirect cost and dependency rows sit at their exact positions.
- [ ] The empty separator rows are still there.
- [ ] `De <= Dn` for every activity.
- [ ] Decimals use a dot, not a comma.
- [ ] The dependency matrix is square and covers every activity.
- [ ] The dependencies contain no cycles.
- [ ] There is at least one activity with no predecessors and at least one with no successors.
