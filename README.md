# JRF Capsidomics Atlas

## Project Overview

A curated, table-driven map of Jelly-Roll Fold (JRF)-containing viral proteins across genome types and hosts, with structural representatives and architecture annotations (T number, capsomer organization, role).

**Objectives:**
1. Produce a master curated database (`jrf_capsidomics_master.xlsx/csv`)
2. Create a high-confidence subset for analysis
3. Generate summary tables/figures (McKenna-style)
4. Build structural similarity clustering/tree + PFAM co-occurrence network (Aguilar-style)
5. Develop a conceptual evolutionary schematic

---

## Directory Structure

```
JRF_Capsidomics_Atlas/
├── README.md                    # This file
├── SCHEMA_DEFINITIONS.md        # Operational definitions
├── lit/                         # Literature references and key papers
├── data_raw/                    # Raw downloaded data
├── data_clean/                  # Cleaned and processed data
├── analyses/                    # Analysis outputs
├── figures/                     # Generated figures
└── scripts/                     # Python/R scripts for each phase
    ├── phase0_setup.py
    ├── phase1_seed_set.py
    ├── phase2_pfam_mapping.py
    ├── phase3_expansion.py
    ├── phase4_annotation.py
    ├── phase5_structural_analysis.py
    └── phase6_visualization.py
```

---

## Workflow Phases

| Phase | Description | Script | Output |
|-------|-------------|--------|--------|
| 0 | Project setup/reproducibility | `phase0_setup.py` | Folder structure, schema |
| 1 | Build gold-standard seed set | `phase1_seed_set.py` | `jrf_seed_set.csv` |
| 2 | Map seeds to PFAM domains | `phase2_pfam_mapping.py` | `jrf_pfam_master.csv` |
| 3 | Expand to all viral proteins | `phase3_expansion.py` | `jrf_all_hits_raw.csv` |
| 4 | McKenna-style annotation | `phase4_annotation.py` | `jrf_capsidomics_master.csv` |
| 5 | Aguilar-style structure analysis | `phase5_structural_analysis.py` | Clustering, networks |
| 6 | Final synthesis | `phase6_visualization.py` | Figures, summary tables |

---

## Quick Start

```bash
# 1. Set up environment
conda create -n jrf_atlas python=3.10 pandas biopython requests networkx matplotlib seaborn scipy
conda activate jrf_atlas

# 2. Run pipeline
cd scripts/
python phase0_setup.py
python phase1_seed_set.py
python phase2_pfam_mapping.py
python phase3_expansion.py
python phase4_annotation.py
python phase5_structural_analysis.py
python phase6_visualization.py
```

---

## Key References

1. **McKenna/Mietzsch** - Parvoviridae structural biology and capsidomics framework
2. **Aguilar et al.** - Structural evolution inference methodology for viral capsid proteins

---

## Master Schema (One Row = One Protein/Domain)

See `SCHEMA_DEFINITIONS.md` for complete field definitions.

### Core Fields:
- `protein_id`: Stable identifier (UniProt preferred)
- `pdb_id`: Representative PDB structure
- `ncbi_id`: NCBI protein accession
- `virus_name`: Virus species/strain
- `protein_name`: Common name (VP1, MCP, etc.)
- `genome_type`: ssDNA, ssRNA+, ssRNA-, dsRNA, dsDNA
- `host_category`: Bacteria, Archaea, Eukaryota (Plant/Animal/Fungi)
- `taxonomy_realm`: Realm → Family lineage
- `architecture_class`: SJR, DJR, tandem_JRF, other
- `capsid_role`: MCP, minor, spike, turret, cement, movement, non-capsid
- `t_number`: T=1, T=3, pseudo-T=3, T=7, higher, NA
- `virion_morphology`: icosahedral, geminate, filamentous, pleomorphic
- `pfam_domains`: Semicolon-separated PFAM accessions
- `evidence_level`: high, medium, low
- `structure_source`: experimental, AlphaFold, homology_model
- `reference_pmid`: Primary literature reference

---

## License

This project is for academic research purposes.
