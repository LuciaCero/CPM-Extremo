# CPM Extremo — Project Cost-Time Analysis

[![CI](https://github.com/LuciaCero/CPM-Extremo/actions/workflows/ci.yml/badge.svg)](https://github.com/LuciaCero/CPM-Extremo/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![NetworkX](https://img.shields.io/badge/NetworkX-3.x-orange)](https://networkx.org/)
[![Tests](https://img.shields.io/badge/tests-pytest-0A9EDC?logo=pytest&logoColor=white)](tests/)

A complete implementation of **CPM crashing** with cost-time analysis. Starting from a table of activities in a spreadsheet, the program builds the project's AOA graph, finds the critical path, iteratively shortens durations in search of the minimum total cost, and produces the full paper trail: charts plus a LaTeX report with every calculation worked out step by step.

*Code identifiers and the generated LaTeX report are in Spanish.*

> Developed as a university project for a Project Planning and Risk Analysis course.

---

## Table of contents

- [What it does](#what-it-does)
- [Sample output](#sample-output)
- [System requirements](#system-requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Input spreadsheet format](#input-spreadsheet-format)
- [Generated output](#generated-output)
- [Running tests](#running-tests)
- [Project structure](#project-structure)
- [How the algorithm works](#how-the-algorithm-works)
- [Notes and limitations](#notes-and-limitations)
- [License](#license)

---

## What it does

| Stage | Description |
|---|---|
| **Reading** | Parses the input spreadsheet: normal and crash durations, normal and crash costs, indirect costs and the dependency matrix. |
| **AOA graph** | Builds the *Activity-on-Arrow* graph, inserts the dummy activities it needs and simplifies away redundant nodes. |
| **Classic CPM** | Computes early and last values for every node, total float, critical activities and every critical path. |
| **CPM crashing** | Iteratively shortens the critical activity with the cheapest cost slope, recomputing the whole CPM at each step. |
| **Cost-time** | Evaluates direct plus indirect cost at every iteration and pinpoints the optimum, the minimum total cost. |
| **Documentation** | Exports the AOA graph, a Gantt chart, the cost-time curve and a LaTeX report with all the working shown. |

One thing that sets this apart from a minimal implementation: **every calculation records its own symbolic and numeric working**. The report does not just show the result `E4 = 14`, it shows the full expression `E4 = Max{E2 + B, E3 + C} = Max{6 + 8, 6 + 5} = Max{14, 11} = 14`, so the exercise can be marked by hand and every step verified.

---

## Sample output

Running `inputs/ejemplo1.xlsx`:

| AOA graph | Cost-time curve |
|:---:|:---:|
| ![AOA graph](output/ejemplo1/output_graph.png) | ![Cost-time curve](output/ejemplo1/output_coste-tiempo.png) |
| *Dummy activities drawn dashed* | *Optimum marked in red* |

![Gantt chart](output/ejemplo1/output_gantt.png)

*Gantt chart of the optimal iteration: red for critical activities, blue for the rest.*

The full LaTeX report for this example lives in [`output/ejemplo1/output_pert.txt`](output/ejemplo1/output_pert.txt).

---

## System requirements

| Requirement | Version | What for |
|---|---|---|
| **Python** | 3.12 | The project's interpreter. |
| **pygraphviz** | 2.0+ | Rendering the AOA graph. Wheels from version 2.0 onwards bundle Graphviz, so there is nothing to install separately. |
| **Kaleido** | 0.2+ | Exporting the Plotly figures to PNG. Installed via `pip`. |

### About Graphviz

`pygraphviz` historically required **Graphviz installed on the system** and reachable on the PATH, and failed to compile without it. Since **version 2.0** it publishes prebuilt wheels for Windows, macOS and Linux that already bundle Graphviz, so `pip install -r requirements.txt` is all it takes and nothing else needs installing.

<details>
<summary><strong>If pip has to build pygraphviz from source</strong></summary>

This happens on platforms with no wheel available, or if a version earlier than 2.0 is pinned. In that case Graphviz and a C compiler are genuinely required:

| Requirement | Minimum version |
|---|---|
| Graphviz | 2.46 |
| C/C++ compiler | — |

```powershell
winget install graphviz
```

```bash
brew install graphviz
```

```bash
sudo apt-get install graphviz graphviz-dev
```

Check that it ended up reachable:

```bash
dot -V
```

The [official pygraphviz instructions](https://pygraphviz.github.io/documentation/stable/install.html) cover how to point it at Graphviz if it still fails.

</details>

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/LuciaCero/CPM-Extremo.git
```

### 2. Create the virtual environment

On Windows, if you have several Python versions installed, it is worth forcing 3.12:

```powershell
py -3.12 -m venv venv
```

```powershell
venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
python3.12 -m venv venv && source venv/bin/activate
```

### 3. Install the dependencies

```bash
pip install -r requirements.txt
```

### 4. Install the project

Recommended: an editable install. It registers the `cpm-extremo` command and resolves the imports without having to touch `PYTHONPATH`.

```bash
pip install -e .
```

<details>
<summary>Alternative without installing: set <code>PYTHONPATH</code> by hand</summary>

From the project root, in every new terminal session:

```powershell
$env:PYTHONPATH = "$PWD\src"
```

On macOS or Linux:

```bash
export PYTHONPATH="$PWD/src"
```

</details>

---

## Usage

```bash
cpm-extremo inputs/ejemplo1.xlsx
```

Or as a module, without installing the package:

```bash
python -m cpm_extremo.main inputs/ejemplo1.xlsx
```

The program takes **a single argument**: the path to the input spreadsheet. Results are written to `output/<spreadsheet_name>/`, creating the folder if it does not exist and overwriting previous runs of the same input.

### Processing every example at once

On Windows (PowerShell):

```powershell
Get-ChildItem inputs\*.xlsx | ForEach-Object { cpm-extremo $_.FullName }
```

On macOS or Linux:

```bash
for f in inputs/*.xlsx; do cpm-extremo "$f"; done
```

---

## Input spreadsheet format

The spreadsheet must follow a **fixed-position layout**: the reader locates data by row number, not by label. The safest way to create a new input is to duplicate [`inputs/ejemplo1.xlsx`](inputs/ejemplo1.xlsx) and overwrite the values.

The full structure is documented in **[docs/INPUT_FORMAT.md](docs/INPUT_FORMAT.md)**. In summary:

| Row (0-indexed) | Content |
|---|---|
| `0` | **Normal duration** (`Dn`) of each activity. The header row carries the names (`A`, `B`, `C`...). |
| `1` | **Crash duration** (`De`): the technical minimum the activity can be shortened to. |
| `2`–`3` | Separator and header of the cost section. |
| `4` | **Normal cost** (`Cn`): cost of the activity at its normal duration. |
| `5` | **Crash cost** (`Ce`): cost of the activity at its crash duration. |
| `6`–`7` | Separator and header of the indirect cost section. |
| `8` | **Indirect costs** in `A + B·X` form: first column the fixed cost `A`, second the daily cost `B`. An empty cell counts as 0. |
| `9` | Separator. |
| `10` | `Dependencias` header plus the activity names. |
| `11` onwards | **Precedence matrix**: a `1` in the cell at row `A`, column `B` means A precedes B. Empty cells mean no relation. |

### Conventions

- The number of activities is derived by counting the non-empty values in row 0.
- **Successors are computed automatically** by inverting the precedence matrix; there is no need to declare them.
- Durations are expressed in **days**; costs, in **euros**.
- Decimals use a **dot**, not a comma.
- Dependencies cannot form cycles: the program validates the graph and aborts with an error if it finds one.

---

## Generated output

Every run produces four files in `output/<spreadsheet_name>/`:

| File | Content |
|---|---|
| `output_graph.png` | The AOA graph rendered with Graphviz. Real activities as solid lines, dummies as dashed grey ones. |
| `output_gantt.png` | Gantt chart of the **optimal iteration**. Red bars for critical activities, blue for the rest. |
| `output_coste-tiempo.png` | Cost-time curve with the optimum highlighted and annotated. The X axis is inverted, with duration decreasing. |
| `output_pert.txt` | The full LaTeX report. Breakdown below. |

### The `output_pert.txt` report

It is a complete LaTeX document (`llncs` class, using `tikz` and `pgfplots`) covering, **for every iteration of the algorithm**:

- The activity data table: `Dn`, `De`, `Cn`, `Ce`, slopes and dependencies.
- The project's indirect cost parameters.
- The early/last table for every node, plus the symbolic working behind each value.
- The float table, plus the symbolic working behind each `Hij`.
- Critical activities and every critical path.
- Project duration, with the sum of each critical path spelled out.
- Total cost, broken down into direct and indirect.

The optimal iteration is flagged explicitly. At the end, the **cost-time curve drawn in TikZ**, ready to drop into an academic document.

#### How to compile it

The report uses Springer's **LNCS class**, which is **not bundled** with TeX Live or MiKTeX. You need to obtain `llncs.cls` separately:

1. Download the class from [CTAN](https://ctan.org/pkg/llncs) or from the [Springer templates](https://www.springer.com/gp/computer-science/lncs/conference-proceedings-guidelines).
2. Drop `llncs.cls` in the same folder as the `.tex` file.
3. Rename the report to `.tex` and compile:

```bash
cp output/ejemplo1/output_pert.txt informe.tex && pdflatex informe.tex
```

If you would rather not download anything, just replace the first line of the `.tex` with a standard `article` class. The rest of the document compiles unchanged, since no LNCS-specific feature is used.

---

## Running tests

The test suite covers the CPM calculations and the spreadsheet reader. It needs no Graphviz and writes nothing to `output/`.

```bash
pip install -e ".[dev]"
```

```bash
pytest
```

The reference case used across the tests is the project in `inputs/ejemplo1.xlsx`, worked out by hand: 21 days and 5750 € before crashing, an optimum of **19 days and 5650 €**, and a stop after two consecutive cost rises. There are also tests for cyclic dependencies and for a project with two simultaneous critical paths.

---

## Project structure

```
CPM-Extremo/
├── inputs/                          # Input spreadsheets (8 examples, simplest first)
│   ├── ejemplo1.xlsx                #   <- reference template (4 activities)
│   ├── ejemplo2.xlsx
│   ├── ejemplo3.xlsx
│   ├── ejemplo4.xlsx
│   ├── ejemplo5.xlsx
│   ├── ejemplo6.xlsx
│   ├── ejemplo7.xlsx
│   └── ejemplo8.xlsx                #   <- the most complex (10 activities)
│
├── output/                          # Results, one subfolder per input
│   └── <spreadsheet_name>/
│       ├── output_graph.png
│       ├── output_gantt.png
│       ├── output_coste-tiempo.png
│       └── output_pert.txt
│
├── docs/
│   ├── INPUT_FORMAT.md              # Detailed spreadsheet specification
│   └── ALGORITHM.md                 # Mathematical basis and pseudocode
│
├── tests/                           # pytest suite
│   ├── conftest.py                  #   Shared fixtures and reference project
│   ├── test_algoritmo.py            #   End-to-end crashing loop
│   ├── test_cpm_calculos.py         #   Early/last, float, critical paths, costs
│   ├── test_grafo.py                #   AOA graph construction and validation
│   ├── test_leer_excel.py           #   Spreadsheet reader
│   └── test_pendientes.py           #   Cost slopes
│
├── src/cpm_extremo/
│   ├── main.py                      # Entry point and orchestration
│   │
│   ├── input/                       # Spreadsheet reading
│   │   └── leer_excel.py            #   Parsing and DataFrame construction
│   │
│   ├── grafo/                       # AOA graph (networkx.DiGraph)
│   │   ├── constructor.py           #   Construction and cycle validation
│   │   ├── reducir.py               #   Node and dummy simplification
│   │   ├── actualizar.py            #   Propagating new durations
│   │   └── info.py                  #   Dumping nodes and activities to DataFrames
│   │
│   ├── cpm/                         # The method itself
│   │   ├── algoritmo.py             #   Main crashing loop
│   │   ├── estado.py                #   Initial state (durations and costs)
│   │   ├── early_last.py            #   Early and last in topological order
│   │   ├── holguras.py              #   Hij = Lj - Ei - Dij
│   │   ├── camino_critico.py        #   Critical activities and paths
│   │   ├── duracion.py              #   Project duration
│   │   ├── costes.py                #   Direct and indirect cost
│   │   ├── pendientes.py            #   Slope = (Ce - Cn) / (Dn - De)
│   │   └── reduccion_actividades.py #   Validated one-day crash
│   │
│   ├── output/                      # Result generation
│   │   ├── grafo_png.py             #   Graphviz
│   │   ├── gantt_png.py             #   Plotly
│   │   ├── coste_tiempo_png.py      #   Matplotlib
│   │   ├── latex_informe.py         #   LaTeX report
│   │   └── filesystem.py            #   Folder and path handling
│   │
│   └── shared/
│       └── globales.py              # Symbolic traces of every calculation
│
├── pyproject.toml
├── requirements.txt
├── LICENSE
└── README.md
```

---

## How the algorithm works

Full explanation and pseudocode in **[docs/ALGORITHM.md](docs/ALGORITHM.md)**. In summary:

```
1. Build the AOA graph and simplify it.
2. Initial state: every activity at its normal duration and cost (Dn, Cn).
3. Compute the cost slope of each activity:
       slope = (Ce - Cn) / (Dn - De)
   Infinite if Dn = De, that is, if the activity cannot be crashed.

4. REPEAT:
     a. Compute early and last for every node, in topological order.
     b. Compute float: Hij = Lj - Ei - Dij.  Critical if Hij = 0.
     c. Find the critical paths and the project duration.
     d. Compute the total cost:
            total = sum of activity costs + (fixed cost + duration * daily cost)
     e. Record the iteration in the cost-time history.
     f. If the cost has risen twice in a row, STOP.
     g. Pick the crashable critical activity with the LOWEST slope.
        If there is none, STOP.
     h. Cut one day off its duration; its cost rises by the value of its slope.
        If the crash turns out invalid, flag the activity as non-crashable
        and try again with another one.
     i. Propagate the new durations to the graph.

5. The optimum is the iteration with the minimum total cost.
```

### Stopping criteria

The loop ends on one of two conditions:

1. **Two consecutive cost rises.** Past the minimum, the algorithm carries on for two more iterations so the cost-time curve clearly shows its rising branch.
2. **No crashable critical activities are left**, because they are all at their crash duration already or were flagged as non-crashable.

### Why the optimum is not always the shortest project

Shortening an activity **raises** its direct cost, since more resources have to be paid for, but **lowers** the indirect cost, since there are fewer days of overhead, rent and supervision. Total cost is the sum of both, so it traces a U: it falls while the savings on indirect costs outweigh the premium on direct ones, and rises as soon as that relationship flips. The optimum is the bottom of the U.

---

## Notes and limitations

- **Crashing happens one day per iteration.** No fractional or block crashing is implemented.
- **The critical path can change between iterations**, and there may be several at once. The algorithm recomputes it from scratch at every step, so it handles this correctly.
- **Slope ties:** if two critical activities share the lowest slope, the first one in DataFrame order wins. Arbitrary, but deterministic.
- **Extra iterations past the optimum:** the history includes two iterations beyond the minimum. They are there on purpose, to complete the curve; they are not a convergence bug.
- **The spreadsheet layout is rigid**, with fixed row positions. A misaligned input does not raise a clear error, it produces wrong results. Always start from the sample file.
- **The AOA graph is not unique.** Different valid constructions, with different numbers of dummy activities, can represent the same project. Early, last, float and duration do not change, but the node numbering may not match a solution worked out by hand.

### About the data in `inputs/`

The files in `inputs/` hold **entirely fictional** data taken from classroom exercises. They are included purely as examples of the input format and so the repository's output can be reproduced. They record no real information about any project, company or person.

---

## License

Released under the MIT License. See [LICENSE](LICENSE) for the full text.
