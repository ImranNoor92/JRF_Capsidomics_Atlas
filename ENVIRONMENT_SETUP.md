# JRF Capsidomics Atlas — Environment Setup

Step-by-step terminal commands to set up a fresh Unix/WSL environment from
`environment.yml`. Run each command block directly in your terminal.

---

## Prerequisites

A Unix terminal is required: native Linux, macOS Terminal, or Windows Subsystem
for Linux (WSL).

On Windows, open your WSL terminal and navigate to the project folder:

```bash
cd /mnt/c/Users/<your_username>/Documents/JRF_Capsidomics_Atlas
```

---

## Step 1 — Install Miniconda

> Skip this step if `conda --version` already returns a version number.

Download the Miniconda installer:

```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh
```

Run the silent install into your home directory:

```bash
bash ~/miniconda.sh -b -p ~/miniconda3
```

Initialize conda for your bash shell:

```bash
~/miniconda3/bin/conda init bash
```

Reload your shell so conda is available immediately:

```bash
source ~/.bashrc
```

Confirm conda is working:

```bash
conda --version
```

Remove the installer to save space:

```bash
rm ~/miniconda.sh
```

---

## Step 2 — Create the conda environment

Run this from the project root (the folder containing `environment.yml`):

```bash
conda env create -f environment.yml
```

This installs Python 3.10 and all project dependencies into an isolated
environment named `jrf_atlas`.

---

## Step 3 — Activate the environment

```bash
conda activate jrf_atlas
```

Your prompt should change to show `(jrf_atlas)` at the start.

---

## Step 4 — Verify the installation

Check Python version:

```bash
python --version
```

List all installed packages:

```bash
conda list
```

Confirm all core imports work:

```bash
python -c "import pandas, numpy, requests, scipy, networkx, matplotlib, seaborn, Bio, openpyxl, xlsxwriter; print('pandas', pandas.__version__); print('numpy', numpy.__version__); print('scipy', scipy.__version__); print('All imports OK')"
```

---

## Step 5 — Run the pipeline

Always run scripts from the project root, not from inside `scripts/`:

```bash
python scripts/phase1_seed_set.py
python scripts/phase2_pfam_mapping.py
python scripts/phase3_expansion.py
python scripts/phase4_annotation.py
python scripts/phase5_structural_analysis.py
python scripts/phase6_visualization.py
```

---

## Every new session

Activate the environment before running any scripts:

```bash
conda activate jrf_atlas
```

---

## Updating after pulling new changes

If `environment.yml` changes, sync your environment:

```bash
conda env update -f environment.yml --prune
```

---

## Removing and rebuilding from scratch

```bash
conda deactivate
conda env remove -n jrf_atlas
conda env create -f environment.yml
conda activate jrf_atlas
```

---

## Packages installed

| Package | Min Version | Purpose |
|---|---|---|
| pandas | 1.5 | DataFrames, CSV I/O |
| numpy | 1.21 | Arrays, matrix operations |
| requests | 2.28 | HTTP calls to UniProt, InterPro, PDB APIs |
| biopython | 1.79 | Sequence parsing |
| scipy | 1.9 | Clustering, distance matrices |
| networkx | 2.8 | Protein similarity networks |
| matplotlib | 3.6 | Figures, heatmaps |
| seaborn | 0.12 | Statistical visualisations |
| openpyxl | 3.0 | Read/write `.xlsx` files |
| xlsxwriter | 3.0 | Excel export with formatting |

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `conda: command not found` | Run `source ~/.bashrc` or restart the terminal |
| `ModuleNotFoundError: No module named 'pandas'` | Run `conda activate jrf_atlas` first |
| Wrong package versions loading | User-level pip packages may override conda. The env activation hook sets `PYTHONNOUSERSITE=1` automatically to prevent this |
| `conda env create` fails with solver error | Run `conda update conda` then retry |
| Wrong Python in VS Code | Command Palette → **Python: Select Interpreter** → choose `~/miniconda3/envs/jrf_atlas/bin/python` |

---

## Verified environment snapshot (2026-03-03)

Built and tested on WSL Ubuntu (Linux x86-64):

| Package | Installed Version |
|---|---|
| python | 3.10.19 |
| pandas | 2.3.3 |
| numpy | 2.2.5 |
| requests | 2.32.5 |
| scipy | 1.15.3 |
| networkx | 3.4.2 |
| matplotlib | 3.10.8 |
| seaborn | 0.13.2 |
| biopython | 1.86 |
| openpyxl | 3.1.5 |
| xlsxwriter | 3.2.9 |
