# JRF Capsidomics Atlas - Step-by-Step Workflow Guide

## Complete Pipeline Documentation

This guide provides detailed step-by-step instructions for building the JRF Capsidomics Atlas, from project setup to final visualization.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Phase 0: Project Setup](#phase-0-project-setup)
4. [Phase 1: Build Seed Set](#phase-1-build-seed-set)
5. [Phase 2: PFAM Mapping](#phase-2-pfam-mapping)
6. [Phase 3: Database Expansion](#phase-3-database-expansion)
7. [Phase 4: Capsidomics Annotation](#phase-4-capsidomics-annotation)
8. [Phase 5: Structural Analysis](#phase-5-structural-analysis)
9. [Phase 6: Visualization & Synthesis](#phase-6-visualization--synthesis)
10. [Troubleshooting](#troubleshooting)
11. [References](#references)

---

## Prerequisites

### Required Software

```bash
# Python 3.8+ with pip
python --version  # Should be 3.8 or higher

# Recommended: Create a dedicated conda environment
conda create -n jrf_atlas python=3.10
conda activate jrf_atlas
```

### Required Python Packages

```bash
# Core packages
pip install pandas numpy requests biopython

# Analysis packages
pip install scipy networkx

# Visualization packages
pip install matplotlib seaborn

# Optional: for Excel export
pip install openpyxl xlsxwriter
```

### Optional External Tools

For advanced structural analysis (Phase 5):

```bash
# TM-align for structural comparisons
# Download from: https://zhanggroup.org/TM-align/
# Add to PATH after installation
```

---

## Quick Start

```bash
# 1. Navigate to project directory
cd /path/to/JRF_Capsidomics_Atlas

# 2. Activate environment
conda activate jrf_atlas

# 3. Run all phases sequentially
cd scripts/
python phase1_seed_set.py
python phase2_pfam_mapping.py
python phase3_expansion.py
python phase4_annotation.py
python phase5_structural_analysis.py
python phase6_visualization.py

# 4. View results
ls ../data_clean/
ls ../analyses/
ls ../figures/
```

---

## Phase 0: Project Setup

### Directory Structure

The project uses this structure:

```
JRF_Capsidomics_Atlas/
├── README.md                    # Project overview
├── SCHEMA_DEFINITIONS.md        # Data dictionary
├── WORKFLOW_GUIDE.md           # This document
├── lit/                        # Literature PDFs and notes
├── data_raw/                   # Raw downloaded data
│   ├── jrf_seed_set.csv       # Phase 1 output
│   ├── jrf_pfam_master.csv    # Phase 2 output
│   └── jrf_all_hits_raw.csv   # Phase 3 output
├── data_clean/                 # Cleaned data
│   ├── jrf_all_hits_clean.csv
│   ├── jrf_capsidomics_master.csv
│   └── jrf_high_confidence.csv
├── analyses/                   # Analysis outputs
│   ├── structural_similarity_matrix.csv
│   ├── pfam_cooccurrence_network.json
│   └── summary_*.csv
├── figures/                    # Generated figures
│   ├── *.png                  # Publication figures
│   └── evolutionary_schematic.txt
└── scripts/                    # Python scripts
    ├── phase1_seed_set.py
    ├── phase2_pfam_mapping.py
    ├── phase3_expansion.py
    ├── phase4_annotation.py
    ├── phase5_structural_analysis.py
    └── phase6_visualization.py
```

### Key Definitions

Review `SCHEMA_DEFINITIONS.md` for:
- SJR vs DJR classification criteria
- Evidence level definitions (high/medium/low)
- Capsid role vocabulary
- T-number standards

---

## Phase 1: Build Seed Set

### Purpose
Create a literature-grounded "gold standard" set of confirmed JRF capsid proteins.

### What It Does
1. Defines ~30 representative JRF proteins across:
   - ssDNA viruses (Parvoviridae, Circoviridae, Geminiviridae)
   - ssRNA viruses (Picornaviridae, Nodaviridae, Tombusviridae)
   - dsDNA viruses (Adenoviridae, Tectiviridae, NCLDVs)
   - JRF-derived non-capsid proteins

2. Records key metadata:
   - Virus name and family
   - Protein name and role
   - PDB structure codes
   - UniProt accessions
   - Architecture class (SJR/DJR)
   - T-number

### How to Run

```bash
cd scripts/
python phase1_seed_set.py
```

### Expected Output

```
data_raw/jrf_seed_set.csv
data_raw/jrf_seed_set_summary.json
```

### Verification

```python
import pandas as pd
df = pd.read_csv('../data_raw/jrf_seed_set.csv')
print(f"Seed proteins: {len(df)}")
print(f"Families: {df['family'].nunique()}")
print(f"With PDB: {len(df[df['primary_pdb'] != ''])}")
```

### Optional: Enrich with UniProt Data

Edit `phase1_seed_set.py` and uncomment this line:
```python
# df = enrich_with_uniprot(df)
```

⚠️ **Note**: This makes ~30 API calls and takes 1-2 minutes.

---

## Phase 2: PFAM Mapping

### Purpose
Map seed proteins to PFAM domain annotations to identify JRF-associated domains.

### What It Does
1. Creates a curated list of JRF PFAM domains:
   - Capsid domains (PF00729, PF00740, PF00608, etc.)
   - Non-capsid JRF-derived domains
   - Classification (SJR/DJR/JRF_derived)

2. Maps each seed protein to its PFAM domains
3. Identifies any unmapped domains for manual curation

### How to Run

```bash
python phase2_pfam_mapping.py
```

### Expected Output

```
data_raw/jrf_pfam_master.csv         # Master PFAM reference
data_raw/seed_to_pfam_mapping.csv    # Seed-PFAM associations
data_raw/jrf_pfam_master_summary.json
```

### Understanding the PFAM Master Table

Key columns:
- `pfam_id`: PFAM accession (PF00740)
- `pfam_name`: Human-readable name
- `jrf_class`: SJR, DJR, or JRF_derived
- `capsid_role`: MCP, minor, spike, etc.
- `is_capsid_pfam`: Boolean for filtering

### Optional: API-Based PFAM Mapping

To query InterPro/UniProt APIs for PFAM annotations:
1. Uncomment API calls in the script
2. Expect ~1 minute for 30 proteins

---

## Phase 3: Database Expansion

### Purpose
Expand from the curated PFAMs to identify ALL viral proteins containing JRF domains.

### What It Does
1. For each PFAM in the master table:
   - Query UniProt/InterPro for viral proteins
   - Filter to virus taxonomy only
   - Collect protein metadata

2. Clean and deduplicate:
   - Remove fragments (< 100 aa)
   - Remove oversized entries (> 2000 aa)
   - Deduplicate by UniProt ID

### How to Run

```bash
# Demo mode (simulated data, fast)
python phase3_expansion.py

# Full mode (real API calls, ~5-10 min per PFAM)
python phase3_expansion.py --use-api
```

### Expected Output

```
data_raw/jrf_all_hits_raw.csv
data_clean/jrf_all_hits_clean.csv
data_clean/jrf_expansion_summary.json
```

### Scaling Considerations

For full expansion:
- ~15 capsid PFAMs × 100-10,000 proteins each
- Total: 10,000 - 100,000+ proteins
- Time: 30-60 minutes
- API rate limiting: 1 request/second

---

## Phase 4: Capsidomics Annotation

### Purpose
Add McKenna/Mietzsch-style capsidomics annotations to create the structured atlas.

### What It Does
1. Adds capsidomics fields:
   - `capsid_role`: MCP, minor, spike, turret, cement, movement
   - `architecture_class`: SJR, DJR, tandem_JRF
   - `virion_morphology`: icosahedral, geminate, filamentous
   - `t_number`: T=1, T=3, pseudo-T=3, T=7, etc.
   - `genome_type`: ssDNA, ssRNA+, dsDNA, dsRNA
   - `jrf_orientation`: tangential vs perpendicular

2. Infers annotations from:
   - Virus family lookup tables
   - Protein name pattern matching
   - PFAM-based classification

3. Applies evidence rules:
   - High: known capsid + correct PFAM + reasonable length
   - Medium: partial evidence
   - Low: sequence similarity only

### How to Run

```bash
# Standard run
python phase4_annotation.py

# With structure lookups (slower, queries PDB/AlphaFold)
python phase4_annotation.py --lookup-structures
```

### Expected Output

```
data_clean/jrf_capsidomics_master.csv    # Full annotated database
data_clean/jrf_high_confidence.csv       # High-confidence subset
data_clean/jrf_capsidomics_summary.json  # Statistics
```

### The Master Table Schema

Key columns in `jrf_capsidomics_master.csv`:

| Column | Description | Example |
|--------|-------------|---------|
| protein_id | UniProt accession | P03135 |
| organism | Virus name | Adeno-associated virus 2 |
| inferred_family | Virus family | Parvoviridae |
| capsid_role | Protein role | MCP |
| architecture_class | JRF type | SJR |
| t_number | Triangulation number | pseudo-T=3 |
| genome_type | Genome classification | ssDNA |
| evidence_level | Confidence | high |

---

## Phase 5: Structural Analysis

### Purpose
Perform Aguilar-style structural evolution analysis.

### What It Does
1. **Structural similarity matrix**: 
   - Compare representative structures
   - Calculate TM-scores (or simulated values)
   - Create similarity heatmap

2. **Hierarchical clustering**:
   - Cluster by structural similarity
   - Identify structural families
   - Generate dendrogram

3. **PFAM co-occurrence network**:
   - Nodes = PFAM domains
   - Edges = co-occurrence in same protein
   - Identifies hybrid architectures

4. **Evolutionary inference**:
   - Propose SJR → DJR transitions
   - Identify neofunctionalization events
   - Map structural lineages

### How to Run

```bash
# Demo mode (simulated TM-scores)
python phase5_structural_analysis.py

# With real TM-align (requires TMalign in PATH)
python phase5_structural_analysis.py --use-tmalign
```

### Expected Output

```
analyses/structural_similarity_matrix.csv
analyses/structure_clustering.json
analyses/pfam_cooccurrence_network.json
analyses/evolutionary_transitions.json
figures/structural_similarity_heatmap.png
figures/structure_dendrogram.png
```

### Installing TM-align (Optional)

```bash
# Download from https://zhanggroup.org/TM-align/
# Compile and install
cd TMalign/
g++ -O3 -o TMalign TMalign.cpp
sudo mv TMalign /usr/local/bin/
```

---

## Phase 6: Visualization & Synthesis

### Purpose
Generate publication-quality figures and summary tables.

### What It Does
1. **Summary tables**:
   - Family overview (protein counts, structures, architecture)
   - Architecture summary
   - Genome × architecture cross-tabulation

2. **Figures**:
   - Architecture distribution pie chart
   - Genome type bar chart
   - T-number distribution
   - Genome × architecture heatmap
   - Top families bar chart

3. **Evolutionary schematic**:
   - ASCII art of JRF lineage relationships
   - SJR → DJR duplication hypothesis
   - Neofunctionalization pathways

### How to Run

```bash
python phase6_visualization.py
```

### Expected Output

```
analyses/summary_family_overview.csv
analyses/summary_architecture.csv
analyses/genome_architecture_matrix.csv
analyses/final_summary_statistics.json

figures/architecture_distribution.png
figures/genome_type_distribution.png
figures/t_number_distribution.png
figures/genome_architecture_heatmap.png
figures/family_overview.png
figures/evolutionary_schematic.txt
```

---

## Post-Pipeline Analysis

### Export to Excel

```python
import pandas as pd

# Load master table
df = pd.read_csv('data_clean/jrf_capsidomics_master.csv')

# Export to Excel with multiple sheets
with pd.ExcelWriter('jrf_capsidomics_atlas.xlsx') as writer:
    df.to_excel(writer, sheet_name='Master', index=False)
    
    # High confidence only
    hc = df[df['evidence_level'] == 'high']
    hc.to_excel(writer, sheet_name='High_Confidence', index=False)
    
    # Summary by family
    family_summary = df.groupby('inferred_family').size().reset_index(name='count')
    family_summary.to_excel(writer, sheet_name='By_Family', index=False)
```

### Query Examples

```python
import pandas as pd
df = pd.read_csv('data_clean/jrf_capsidomics_master.csv')

# All parvoviruses
parvos = df[df['inferred_family'] == 'Parvoviridae']

# All DJR proteins
djr = df[df['architecture_class'] == 'DJR']

# High-confidence MCPs with structures
mcp_struct = df[
    (df['capsid_role'] == 'MCP') & 
    (df['evidence_level'] == 'high') &
    (df['structure_id'].notna())
]

# Cross-tabulation
pd.crosstab(df['genome_type'], df['architecture_class'])
```

---

## Troubleshooting

### Common Issues

**1. API Rate Limiting**
```
Error: HTTP 429 Too Many Requests
```
Solution: Increase `rate_limit` parameter in scripts (default: 0.5-1.0 seconds)

**2. Missing Dependencies**
```
ModuleNotFoundError: No module named 'networkx'
```
Solution: `pip install networkx`

**3. No Data Files Found**
```
Error: Seed set not found
```
Solution: Run phases in order (1 → 2 → 3 → 4 → 5 → 6)

**4. TM-align Not Found**
```
Warning: TM-align not found. Using simulated scores.
```
Solution: Install TM-align or use demo mode (simulated values are reasonable approximations)

**5. Empty Figures**
```
Warning: Matplotlib not available
```
Solution: `pip install matplotlib seaborn`

### Validating Results

```python
# Quick validation script
import pandas as pd
import json

# Check all expected files exist
from pathlib import Path

expected_files = [
    'data_raw/jrf_seed_set.csv',
    'data_raw/jrf_pfam_master.csv',
    'data_clean/jrf_capsidomics_master.csv',
    'analyses/final_summary_statistics.json'
]

for f in expected_files:
    path = Path(f)
    if path.exists():
        print(f"✓ {f}")
    else:
        print(f"✗ {f} MISSING")

# Load and validate master table
df = pd.read_csv('data_clean/jrf_capsidomics_master.csv')
print(f"\nMaster table: {len(df)} entries")
print(f"Columns: {list(df.columns)}")
print(f"Architecture classes: {df['architecture_class'].unique()}")
```

---

## References

### Key Literature

1. **McKenna R et al.** (Parvoviridae capsidomics framework)
   - Structural biology of AAV and parvoviruses
   - T-number and capsid architecture definitions

2. **Mietzsch M et al.** (Parvovirus structural atlas)
   - Comprehensive structural catalog
   - Variable region annotations

3. **Aguilar C et al.** (Structural evolution methodology)
   - Fold-driven evolutionary inference
   - Structure > sequence phylogeny

4. **Krupovic M, Bamford DH** (PRD1-Adenovirus lineage)
   - DJR evolution hypothesis
   - Vertical inheritance across domains

### Databases Used

- **UniProt**: https://www.uniprot.org
- **InterPro/PFAM**: https://www.ebi.ac.uk/interpro
- **PDB**: https://www.rcsb.org
- **AlphaFold**: https://alphafold.ebi.ac.uk

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-27 | Initial release |

---

## Contact

For questions or issues, please refer to the project repository or open an issue.
