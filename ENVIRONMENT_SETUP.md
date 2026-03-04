# Environment Setup Guide

This document explains how to set up the Python environment needed to run the
**JRF Capsidomics Atlas** pipeline on any machine.

---

## Quick Start (recommended)

```bash
# 1. Clone the repository
git clone https://github.com/ImranNoor92/JRF_Capsidomics_Atlas.git
cd JRF_Capsidomics_Atlas

# 2. Create the conda environment from the lock file
conda env create -f environment.yml

# 3. Activate it
conda activate jrf_atlas

# 4. Run the pipeline
python scripts/phase1_seed_set.py
```

---

## What Is Installed and Why

### Runtime (Python 3.10)

The environment is pinned to **Python 3.10** for compatibility with all
dependencies. The table below lists every third-party package the scripts import
and which phases use it.

| Package | Min Version | Used By | Purpose |
|---|---|---|---|
| **pandas** | 1.5 | All phases (1–6) | DataFrames, CSV I/O, data wrangling |
| **numpy** | 1.21 | Phases 1, 5, 6 | Numerical arrays, matrix operations |
| **requests** | 2.28 | Phases 1–3 | HTTP calls to UniProt, InterPro, PDB APIs |
| **biopython** | 1.79 | Phases 3–5 | Sequence parsing, BLAST helpers |
| **scipy** | 1.9 | Phase 5 | Hierarchical clustering, distance matrices |
| **networkx** | 2.8 | Phase 5 | Protein similarity networks |
| **matplotlib** | 3.6 | Phase 6 | Plotting (figures, heatmaps) |
| **seaborn** | 0.12 | Phase 6 | Statistical visualisations |
| **openpyxl** | 3.0 | Phase 4 (optional) | Read/write `.xlsx` files |
| **xlsxwriter** | 3.0 | Phase 6 (optional) | Excel export with formatting |

The remaining imports (`json`, `logging`, `pathlib`, `typing`, `collections`,
`gzip`, `io`, `re`, `os`, `subprocess`, `time`) are **Python standard library**
modules and require no installation.

---

## Installation Methods

### Option A — Conda (recommended)

Conda handles compiled C/Fortran libraries (numpy, scipy) automatically and
avoids the "externally-managed-environment" error seen with Homebrew Python on
macOS.

```bash
conda env create -f environment.yml   # first time
conda activate jrf_atlas
```

To update after pulling new changes:

```bash
conda env update -f environment.yml --prune
```

### Option B — pip + venv

If you don't use conda:

```bash
python3.10 -m venv .venv
source .venv/bin/activate          # macOS / Linux
# .venv\Scripts\activate           # Windows
pip install -r requirements.txt
```

> **Note:** On macOS with Homebrew Python you *must* use a virtual environment.
> Running `pip install` outside a venv will fail with a PEP 668
> "externally-managed-environment" error.

---

## Running the Scripts

**Always run from the project root**, not from inside `scripts/`:

```bash
cd JRF_Capsidomics_Atlas

python scripts/phase1_seed_set.py
python scripts/phase2_pfam_mapping.py
python scripts/phase3_expansion.py
python scripts/phase4_annotation.py
python scripts/phase5_structural_analysis.py
python scripts/phase6_visualization.py
```

Running from inside `scripts/` can cause numpy import conflicts because Python
may pick up local directories that shadow installed packages.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'pandas'` | Activate the environment first: `conda activate jrf_atlas` |
| `ImportError: … numpy … should not try to import numpy from its source directory` | `cd` to the project root before running scripts |
| `error: externally-managed-environment` (macOS) | Use conda or a `python -m venv` virtual environment instead of bare `pip` |
| Wrong Python used by VS Code | Open Command Palette → **Python: Select Interpreter** → choose `jrf_atlas` |
| `conda: command not found` | Install [Miniconda](https://docs.anaconda.com/miniconda/) or [Anaconda](https://www.anaconda.com/download) |

---

## Verifying the Environment

After activation, confirm everything is importable:

```bash
python -c "
import pandas, numpy, requests
print(f'pandas  {pandas.__version__}')
print(f'numpy   {numpy.__version__}')
print(f'requests {requests.__version__}')
print('All core imports OK')
"
```

---

## Current Snapshot (as of 2026-03-03)

Captured from the working `jrf_atlas` environment on macOS (Apple Silicon via
Rosetta / x86 conda):

| Package | Installed Version |
|---|---|
| python | 3.10.18 |
| pandas | 2.3.1 |
| numpy | 2.0.1 |
| requests | 2.32.4 |
| conda | 24.9.2 |
