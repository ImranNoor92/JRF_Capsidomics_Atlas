# JRF Capsidomics Atlas — Master From-Scratch Workflow

## Document Purpose

This is the **definitive, granular, step-by-step** workflow for building the JRF Capsidomics Atlas from zero data to a publishable dataset + structural evolutionary analysis. Every step is the smallest actionable unit. Nothing is assumed to exist yet.

**Current repo status (as of audit):**
- Phase 1 seed set: 30 real literature-sourced proteins hardcoded → real
- Phases 2–6: code scaffolded but outputs are **simulated demo data**
- Papers folder: 9 key PDFs (McKenna/Mietzsch, Aguilar et al., Krupovic, etc.) ✓
- No real expanded dataset, no real structural comparisons, no real PFAM network

**Goal:** Replace all simulated outputs with real, defensible data.

---

## Architecture Overview

```
PHASE 0   Project setup / environment / definitions
    ↓
PHASE 1   Gold-standard seed set (literature extraction)          ~30-50 proteins
    ↓
PHASE 2   PFAM domain mapping (seed → PFAM domains)               ~15-25 PFAMs
    ↓
PHASE 3   Database expansion (PFAM → all viral proteins)           ~500-5000 hits
    ↓
PHASE 4   Capsidomics annotation (McKenna-style fields)            master.csv
    ↓
PHASE 5   Structural analysis (Aguilar-style inference)            trees, networks
    ↓
PHASE 6   Visualization, synthesis & figures                       publication ready
```

**Time estimate:** 4–8 weeks for a careful, thorough build. Can be compressed to 2–3 weeks with focused effort.

---

# ═══════════════════════════════════════════════════════════════════
# PHASE 0 — PROJECT SETUP & REPRODUCIBILITY
# ═══════════════════════════════════════════════════════════════════

## 0.1 — Create the Conda Environment

**Why:** Isolate dependencies so results are reproducible.

```bash
conda create -n jrf_atlas python=3.10
conda activate jrf_atlas
pip install pandas numpy requests biopython scipy networkx matplotlib seaborn openpyxl xlsxwriter
```

**Verify:**
```bash
python -c "import pandas, numpy, requests, Bio, scipy, networkx, matplotlib, seaborn; print('All good')"
```

## 0.2 — Verify Folder Structure

```bash
cd /path/to/JRF_Capsidomics_Atlas
ls papers/          # Should show 9 PDFs
ls scripts/         # Should show phase1–phase6 .py files
ls data_raw/        # Will have seed_set.csv (demo), to be replaced
ls data_clean/      # Demo files, to be replaced
ls analyses/        # Demo files, to be replaced
```

## 0.3 — Read and Internalize the Schema

Open `SCHEMA_DEFINITIONS.md`. Commit these definitions to memory (or print):

| Field                | Possible Values                                           | Notes                                      |
|----------------------|-----------------------------------------------------------|--------------------------------------------|
| `architecture_class` | SJR, DJR, tandem_JRF, JRF_hybrid, nucleoplasmin_like     | SJR vs DJR is the primary axis             |
| `capsid_role`        | MCP, minor, spike, turret, cement, movement, non-capsid   | MCP = major capsid protein                 |
| `t_number`           | T=1, T=3, pseudo-T=3, T=7, T=13, T=25, higher, NA       | Triangulation number of icosahedral shell  |
| `virion_morphology`  | icosahedral, geminate, prolate, filamentous, pleomorphic  | Particle shape                             |
| `genome_type`        | ssDNA, dsDNA, ssRNA+, ssRNA-, dsRNA                       | Baltimore class                            |
| `evidence_level`     | high, medium, low                                         | Defined by checklist in SCHEMA_DEFINITIONS |
| `host_category`      | Bacteria, Archaea, Eukaryota_Animal/Plant/Fungi/Protist   | Broad host classification                  |

## 0.4 — Read the Key Papers (Literature Foundation)

You **must** read (at least skim) these before proceeding. The science drives every decision.

| # | Paper (from your papers/ folder)                                              | What You Extract                                                                                             |
|---|-------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------|
| 1 | `structural_capsidomics_of_single_stranded_dna.pdf`                           | McKenna/Mietzsch framework: how to build a capsidomics table for ssDNA capsids. Copy their table structure.  |
| 2 | `anatomy_and_evolution_of_Proteins_displaying_the_Viral_Capsid_Jell_roll...`  | **Aguilar et al. (2025) — your methodological blueprint.** Fold-level relationships, domain networks, transitions. |
| 3 | `the_so_far_farthest_reaches_of_the_double_jelly_roll...`                     | DJR lineage breadth: which families, which hosts, which architectures. Extend your DJR seed list from here.  |
| 4 | `multiple_origins_of_viral_capsid_proteins_from_cellular_ancestors.pdf`        | Multiple origin hypothesis — important for framing your evolutionary schematic.                               |
| 5 | `viral_capsid_proteins_are_segregated_in_structural_fold_space.pdf`            | Fold-space segregation — how JRF relates to HK97 fold and other capsid folds.                                |
| 6 | `cellular_homologs_of_the_double_jelly_roll.pdf`                              | DJR in cellular proteins — relevant for "JRF-derived non-capsid" category.                                   |
| 7 | `global_organization_and_proposed_megataxonomy_of_the_virus_world.pdf`         | Realm/kingdom taxonomy framework — use for standardized taxonomy column.                                     |
| 8 | `the_diversity_of_protein_protein_interaction_interfaces_within=T=3...`        | T=3 interface diversity — useful for understanding SJR capsid assembly variability.                           |
| 9 | `small_viruses_reveal_bidirectional_evolution_between_HK97_fold...`            | HK97 ↔ encapsulin connections — relevant for placing JRF in broader fold context.                            |

### 0.4.1 — Create a Literature Notes Sheet

Create `papers/literature_extraction_notes.md`:

```markdown
# Literature Extraction Notes

## From McKenna/Mietzsch (Structural Capsidomics of ssDNA)
### Supplementary tables extracted:
- Table S1: [list viruses, PDBs, T-numbers]
- Table S2: [...]
### Key structural representatives I will use as seeds:
- [...]

## From Aguilar et al. (2025)
### Methodology I will replicate:
- Structure comparison method: [TM-align / DALI / Foldseek]
- Domain network construction: [how they built PFAM co-occurrence]
- Evolutionary inference logic: [what transitions they identified]
### Figures to emulate:
- Fig X: structural tree of [...]
- Fig Y: domain co-occurrence network

## From Krupovic/Bamford (DJR reaches)
### Additional DJR families to include:
- [...]
### New PDB structures for DJR:
- [...]
```

**Action:** Fill this in as you read each paper. This becomes your evidence trail.

## 0.5 — Decide: Which Seed Proteins Are You Confident About?

Review the existing 30-seed list in `data_raw/jrf_seed_set.csv`. For each entry ask:
1. Is the PDB code valid? (spot-check 5–10 at https://www.rcsb.org)
2. Is the UniProt ID correct? (spot-check at https://www.uniprot.org)
3. Is the family/architecture classification correct per the papers?
4. Are there additional representatives the papers mention that are missing?

**Output:** A handwritten checklist or markdown file confirming the seed set is correct.

---

# ═══════════════════════════════════════════════════════════════════
# PHASE 1 — BUILD GOLD-STANDARD SEED SET
# ═══════════════════════════════════════════════════════════════════

**Goal:** ~30–50 confirmed JRF capsid proteins, each with verified PDB structure and UniProt accession.

## 1.1 — Extract Seed Proteins from McKenna/Mietzsch Paper

### 1.1.1 — Open the ssDNA capsidomics paper
Open `papers/structural_capsidomics_of_single_stranded_dna.pdf`.

### 1.1.2 — Find supplementary/main tables listing:
- Virus name, family, genome configuration
- Capsid protein name (VP1, VP2, coat protein, etc.)
- PDB codes for solved structures
- T-number / capsid geometry
- Host organism

### 1.1.3 — Manually transcribe or PDF-extract each ssDNA capsid entry
For each virus/protein pair, record:
```
virus_name | protein_name | family | genome_type=ssDNA | PDB | T-number | host | architecture=SJR
```

### 1.1.4 — Cross-check each PDB code
Go to https://www.rcsb.org/structure/XXXX for each code. Verify:
- [ ] The structure exists
- [ ] It is indeed a capsid/coat protein
- [ ] Resolution is reasonable (≤4 Å for X-ray, ≤6 Å for cryo-EM)
- [ ] Record the UniProt accession linked to the PDB entry

### 1.1.5 — Verify UniProt accessions
Go to https://www.uniprot.org/uniprot/XXXXX for each. Verify:
- [ ] The protein is annotated as capsid/coat/structural
- [ ] The organism matches
- [ ] Record protein length and any PFAM annotations shown

**Expected yield:** ~10–15 ssDNA capsid proteins from this paper alone.

## 1.2 — Extract Seed Proteins from ssRNA Virus Structures

### 1.2.1 — Use textbook knowledge + Aguilar et al. tables
Canonical SJR RNA capsid families to include:

| Family          | Representative       | PDB   | Protein  | T-number    |
|-----------------|----------------------|-------|----------|-------------|
| Picornaviridae  | Poliovirus 1         | 1HXS  | VP1      | pseudo-T=3  |
| Picornaviridae  | Rhinovirus 14        | 4RHV  | VP1      | pseudo-T=3  |
| Picornaviridae  | FMDV                 | 1BBT  | VP1      | pseudo-T=3  |
| Nodaviridae     | Nodamura virus       | 1NOV  | Capsid α | T=3         |
| Nodaviridae     | Flock house virus    | 2Z2Q  | Capsid α | T=3         |
| Tombusviridae   | TBSV                 | 2TBV  | Coat     | T=3         |
| Bromoviridae    | CCMV                 | 1CWP  | Coat     | T=3         |
| Birnaviridae    | IBDV                 | 1WCE  | VP2      | T=13        |

### 1.2.2 — Add any additional ssRNA families from Aguilar et al.
Check if they include:
- Caliciviridae (norovirus, T=3)
- Tymoviridae (turnip yellow mosaic virus, T=3)
- Sobemovirus (SBMV)
- Leviviridae (MS2, ssRNA phage, T=3)

For each, find PDB code + UniProt. Add if structure exists.

### 1.2.3 — Cross-check each (same as 1.1.4–1.1.5)

## 1.3 — Extract Seed Proteins from DJR Lineage

### 1.3.1 — Use the DJR reaches paper + Aguilar et al.
Open `the_so_far_farthest_reaches_of_the_double_jelly_roll...pdf`. Extract:

| Family          | Representative       | PDB   | Protein      | T-number    |
|-----------------|----------------------|-------|--------------|-------------|
| Tectiviridae    | PRD1                 | 1W8X  | P3 (MCP)     | pseudo-T=25 |
| Tectiviridae    | Bam35                | 6QVV  | MCP          | pseudo-T=25 |
| Adenoviridae    | HAdV-5               | 1P30  | Hexon        | pseudo-T=25 |
| Phycodnaviridae | PBCV-1               | 1M3Y  | Vp54         | T=169       |
| Asfarviridae    | ASFV                 | 6KU9  | p72          | T=214       |
| Poxviridae      | Vaccinia             | 2YGC  | D13          | NA          |
| Turriviridae    | STIV                 | 2BBD  | B345         | pseudo-T=31 |

### 1.3.2 — Check for additional DJR members mentioned in the paper:
- Marseilleviridae MCPs
- Iridoviridae MCPs (FV3, CIV)
- Mimiviridae MCPs
- Lavidaviridae (virophage) MCPs
- Corticoviridae (PM2)
- Sphaerolipoviridae (archaeal)
- Any new cryo-EM structures published 2023–2025

### 1.3.3 — For each new DJR, verify PDB + UniProt as above

## 1.4 — Add JRF-Derived Non-Capsid Proteins

### 1.4.1 — Movement proteins
From Aguilar et al. and the "multiple origins" paper:
- TMV 30K movement protein (PDB: 1VIM, UniProt: P03583)
- Other plant virus movement proteins if structures exist

### 1.4.2 — Spike/turret/vertex proteins
- PRD1 P5 spike (PDB: 1YQ8)
- Adenovirus penton base (PDB: 1X9T)
- STIV turret protein if available

### 1.4.3 — Cement proteins
- Adenovirus protein IX (PDB: 6CGV region)

### 1.4.4 — Cellular JRF homologs (if in scope)
From `cellular_homologs_of_the_double_jelly_roll.pdf`:
- Nucleoplasmin-like proteins?
- Decide: include or exclude? (Recommend: include as separate category, flag `is_cellular=True`)

## 1.5 — Compile and Validate the Seed Set

### 1.5.1 — Add any new seeds to the SEED_PROTEINS list in `phase1_seed_set.py`
Edit the Python dict literal to add/modify entries. Each entry needs:
```python
{
    "virus_name": "...",
    "virus_abbrev": "...",
    "protein_name": "...",
    "capsid_role": "MCP|minor|spike|turret|cement|movement|non-capsid",
    "genome_type": "ssDNA|dsDNA|ssRNA+|dsRNA",
    "host_category": "Bacteria|Archaea|Eukaryota_Animal|Eukaryota_Plant|...",
    "family": "...",
    "architecture_class": "SJR|DJR|JRF_hybrid|other",
    "t_number": "T=1|T=3|pseudo-T=3|T=7|...|NA",
    "virion_morphology": "icosahedral|geminate|...",
    "pdb_ids": ["XXXX"],
    "uniprot_id": "XXXXXX",
    "reference_pmid": "...",
    "notes": "..."
}
```

### 1.5.2 — Run Phase 1
```bash
cd scripts/
python phase1_seed_set.py
```
Check: `data_raw/jrf_seed_set.csv` should now have your complete seed set.

### 1.5.3 — Enable UniProt enrichment
Uncomment the line `# df = enrich_with_uniprot(df)` in `phase1_seed_set.py` and re-run. This adds protein length, official organism name, taxonomy ID, and review status from UniProt. Takes ~30 seconds for 30 proteins.

### 1.5.4 — Manually review the output CSV
Open in Excel or a viewer. For each row verify:
- [ ] No empty critical fields (protein_id, pdb_ids, family, architecture_class)
- [ ] Architecture class makes biological sense (parvoviruses = SJR, adenoviruses = DJR, etc.)
- [ ] T-numbers are correct per the literature
- [ ] No duplicate entries

### 1.5.5 — Record your final seed count
Target: 30–50 proteins. If fewer than 25, go back to papers and add more. If more than 60, consider whether you're overrepresenting certain families.

---

# ═══════════════════════════════════════════════════════════════════
# PHASE 2 — MAP SEEDS TO PFAM DOMAINS
# ═══════════════════════════════════════════════════════════════════

**Goal:** A curated table of ~15–25 JRF-associated PFAM domains, each classified as capsid vs. non-capsid.

## 2.1 — Understand What PFAM Mapping Means

Each seed protein → search UniProt → see which PFAM domains are annotated → the JRF capsid core will be one specific PFAM domain. You want to collect ALL PFAM IDs that correspond to JRF capsid cores across your seed set.

## 2.2 — Verify the Pre-Curated PFAM List

The existing `phase2_pfam_mapping.py` has `KNOWN_JRF_PFAMS` with ~19 entries. Verify each:

### 2.2.1 — For each PFAM in the list:
Go to https://www.ebi.ac.uk/interpro/entry/pfam/PFXXXXX/

- [ ] Does the domain description match a JRF/capsid protein?
- [ ] Is the `jrf_class` (SJR/DJR) correct?
- [ ] Are the example PDBs valid?
- [ ] How many viral proteins does this PFAM family contain? (recorded on InterPro page)

### 2.2.2 — Check for missing PFAMs
For each seed protein NOT yet mapped to a PFAM in the list:
1. Go to UniProt entry for that protein
2. Look at "Family & Domains" section
3. Find the PFAM accession corresponding to the capsid domain
4. If it's not in `KNOWN_JRF_PFAMS`, add it

### 2.2.3 — Identify borderline/ambiguous PFAMs
Some PFAMs are "JRF-like" but not capsid:
- PF01107 (30K movement protein) → flag as `is_capsid_pfam=False, is_jrf_derived=True`
- PF00927 (Nucleoplasmin) → same treatment
- Any domain found only in cellular proteins → exclude or flag

## 2.3 — Update the PFAM Master Table in Code

### 2.3.1 — Edit `KNOWN_JRF_PFAMS` dict in `phase2_pfam_mapping.py`
Add any new PFAMs discovered in 2.2.2. Remove any that are incorrect.

### 2.3.2 — Run Phase 2
```bash
python phase2_pfam_mapping.py
```
Check outputs:
- `data_raw/jrf_pfam_master.csv` — should list all your curated PFAMs
- `data_raw/seed_to_pfam_mapping.csv` — shows which seeds map to which PFAMs
- `data_raw/jrf_pfam_master_summary.json` — counts

### 2.3.3 — Verify the mapping
Open `seed_to_pfam_mapping.csv`. For each seed:
- [ ] Does it have at least one PFAM assigned?
- [ ] Is the PFAM the correct one? (e.g., Parvo_coat for parvoviruses, not some random domain)
- [ ] Any seeds with NO PFAM match? Investigate manually.

### 2.3.4 — Create PFAM classification tiers

In your notes or in the CSV, label each PFAM:

| Tier | Criteria | Use In Expansion |
|------|----------|-------------------|
| **Tier 1 — Core Capsid** | SJR or DJR MCP, high confidence, ≥2 seed members | YES — primary expansion targets |
| **Tier 2 — Minor Capsid** | Spike, penton, cement, turret PFAMs | YES — expand separately |
| **Tier 3 — JRF-Derived** | Movement proteins, non-capsid functions | MAYBE — expand for completeness, flag differently |
| **Tier 4 — Ambiguous** | Low confidence or only cellular hits | NO — exclude from expansion |

---

# ═══════════════════════════════════════════════════════════════════
# PHASE 3 — EXPAND FROM PFAM TO ALL VIRAL PROTEINS
# ═══════════════════════════════════════════════════════════════════

**Goal:** Use each Tier 1/2 PFAM to pull all matching viral proteins from InterPro/UniProt. This creates your "universe" of JRF capsid candidates.

**⚠️ This is where you replace simulated data with REAL data.**

## 3.1 — Decide Your Expansion Strategy

Two options (can do both):

| Method | Pros | Cons |
|--------|------|------|
| **InterPro API** | Comprehensive, includes all member databases | Complex JSON responses, pagination needed |
| **UniProt search** | Cleaner metadata, reviewed entries available | May miss unreviewed proteins |

**Recommended:** Use UniProt search as primary (cleaner), InterPro as supplementary for completeness.

## 3.2 — Manual Pilot: Test One PFAM Expansion

Before running the script, do ONE expansion manually to understand the data:

### 3.2.1 — Pick a well-known PFAM (e.g., PF00740 = Parvo_coat)
Go to: https://www.ebi.ac.uk/interpro/entry/pfam/PF00740/protein/uniprot/#table

### 3.2.2 — Note how many proteins are listed
Record: "PF00740 has ___ total proteins, ___ are from viruses"

### 3.2.3 — Download 10 entries manually
Click through a few. Note what fields are available: accession, organism, length, status (reviewed/unreviewed), domain boundaries.

### 3.2.4 — Test the UniProt REST API directly
In a browser or curl:
```bash
curl "https://rest.uniprot.org/uniprotkb/search?query=(xref:pfam-PF00740)+AND+(taxonomy_id:10239)&format=tsv&fields=accession,protein_name,organism_name,organism_id,length,xref_pfam&size=10"
```
(taxonomy_id:10239 = all viruses)

Check: Do results look reasonable? Are they viral capsid proteins?

## 3.3 — Run Phase 3 with Real API Calls

### 3.3.1 — Run the expansion
```bash
python phase3_expansion.py --use-api
```

**This will:**
- For each capsid-type PFAM in `jrf_pfam_master.csv`:
  - Query InterPro for all viral protein members
  - Query UniProt as fallback/supplement
- Collect: UniProt ID, protein name, organism, taxonomy ID, protein length, PFAM source, family
- Filter: viruses only, length 80–2000 aa
- Deduplicate by UniProt accession

**Expected time:** 5–20 minutes depending on number of PFAMs and internet speed. The script has rate-limiting built in.

### 3.3.2 — Check raw output
```bash
wc -l ../data_raw/jrf_all_hits_raw.csv  # How many raw hits?
head -20 ../data_raw/jrf_all_hits_raw.csv  # Spot-check entries
```

### 3.3.3 — Evaluate the raw hit count

| Raw Hits | Assessment |
|----------|------------|
| < 100    | Too few — check if API calls succeeded (look at log output). May need to adjust queries. |
| 100–500  | Reasonable for a focused capsid atlas. |
| 500–2000 | Good — comprehensive coverage. |
| > 5000   | May include too many strain variants — need stricter deduplication. |

### 3.3.4 — Check the cleaning report
The script logs: proteins removed (fragments, oversized), duplicates removed. Review these numbers. If >50% were removed, investigate why.

### 3.3.5 — Inspect the clean output
```bash
wc -l ../data_clean/jrf_all_hits_clean.csv
# Open in Excel/pandas:
python -c "
import pandas as pd
df = pd.read_csv('../data_clean/jrf_all_hits_clean.csv')
print('Total:', len(df))
print('By PFAM source:')
print(df['pfam_source'].value_counts())
print('By family:')
print(df['family'].value_counts().head(20))
"
```

### 3.3.6 — Manual quality check: random sample
Pick 10 random entries. For each:
- [ ] Look up UniProt ID — is it a real viral capsid protein?
- [ ] Is the family assignment correct?
- [ ] Is the protein length in a reasonable range for its architecture class?

### 3.3.7 — Handle edge cases
- **If API calls fail:** Check error messages. Common issues: rate limiting (add longer delays), server downtime (wait and retry), query syntax.
- **If too few hits for a PFAM:** The PFAM may be deprecated or merged into InterPro. Check the InterPro page manually.
- **If hits include non-viral proteins:** The taxonomy filter may be too loose. Add stricter tax_id=10239 (Viruses) filtering.

## 3.4 — Optional: Supplement with Literature Proteins

### 3.4.1 — Cross-reference your seed set
Any seed protein NOT recovered by PFAM expansion? Mark these and add manually to the clean hit list.

### 3.4.2 — Add proteins from paper tables
If McKenna/Mietzsch or Aguilar et al. list proteins not caught by PFAM queries (e.g., very recently characterized), add them to `data_raw/jrf_literature_raw.csv` (currently empty header-only) with `source=literature_manual`.

---

# ═══════════════════════════════════════════════════════════════════
# PHASE 4 — McKENNA-STYLE CAPSIDOMICS ANNOTATION
# ═══════════════════════════════════════════════════════════════════

**Goal:** Add all capsidomics fields to every protein in the clean hit list, creating the master database.

## 4.1 — Understand What Needs Annotation

Each protein in `jrf_all_hits_clean.csv` needs these fields added:

| Field | How to Determine | Notes |
|-------|------------------|-------|
| `capsid_role` | Protein name + family rules | MCP, minor, spike, etc. |
| `architecture_class` | PFAM jrf_class → SJR/DJR | Inherited from PFAM master |
| `virion_morphology` | Family → standard morphology | Lookup table |
| `t_number` | Family → standard T-number | Lookup table |
| `genome_type` | Family → genome type | Lookup table |
| `host_category` | Family OR organism name → host | Lookup table + keyword matching |
| `jrf_orientation` | SJR=tangential, DJR=perpendicular | Rule-based |
| `realm` | ICTV taxonomy → realm | Lookup table |
| `structure_source` | PDB/AlphaFold availability | API query |
| `evidence_level` | Checklist scoring | Rule-based |

## 4.2 — Review and Extend the Family Annotation Lookup Tables

### 4.2.1 — Open `phase4_annotation.py`
Find the `FAMILY_ANNOTATIONS` dictionary. It maps family name → default annotation values.

### 4.2.2 — Check coverage
List all unique families in your clean hits:
```python
import pandas as pd
df = pd.read_csv('data_clean/jrf_all_hits_clean.csv')
families = df['family'].unique()
print(f"Unique families: {len(families)}")
for f in sorted(families):
    print(f"  {f}")
```

### 4.2.3 — For each family NOT in FAMILY_ANNOTATIONS:
Research and add:
```python
"NewFamilyName": {
    "genome_type": "???",
    "host_category": "???",
    "virion_morphology": "???",
    "t_number": "???",
    "jrf_orientation": "???",
    "realm": "???",
}
```
Sources: ICTV taxonomy pages (https://ictv.global/taxonomy), ViralZone (https://viralzone.expasy.org/), individual publications.

### 4.2.4 — Handle organisms with unknown/novel families
Some proteins may come from metagenomically-discovered viruses without formal family assignment. Strategy:
- If taxonomy says "unclassified viruses" → set family="Unclassified", leave morphology/T-number as "unknown"
- If partial taxonomy exists (e.g., "Caudovirales") → use order-level classification

## 4.3 — Run Phase 4 (Annotation)

### 4.3.1 — Run without structure lookup first (faster)
```bash
python phase4_annotation.py
```

### 4.3.2 — Check the master output
```python
import pandas as pd
df = pd.read_csv('../data_clean/jrf_capsidomics_master.csv')
print(f"Total entries: {len(df)}")
print(f"\nColumns: {list(df.columns)}")
# Check for missing values
for col in ['capsid_role','architecture_class','genome_type','host_category']:
    missing = df[col].isna().sum() + (df[col]=='').sum() + (df[col]=='unknown').sum()
    print(f"  {col}: {missing} missing/unknown out of {len(df)}")
```

### 4.3.3 — Fix any annotations with high unknown rate
If >20% of entries have "unknown" for a critical field, investigate:
- Is the family lookup table missing entries?
- Are protein names not matching the regex patterns?
- Do you need manual curation for specific families?

### 4.3.4 — Run with structure lookup (optional but recommended)
```bash
python phase4_annotation.py --lookup-structures
```
This queries PDBe and AlphaFold for each UniProt ID. Adds `structure_source` and `structure_id` columns. Takes 5–30 minutes depending on dataset size.

### 4.3.5 — Apply evidence level rules
The script uses `apply_evidence_rules()` to classify each entry as high/medium/low:
- **High:** Annotated as capsid in UniProt + correct capsid PFAM + reasonable length + structure available
- **Medium:** Two of the above criteria
- **Low:** Only sequence similarity

Check the distribution:
```python
print(df['evidence_level'].value_counts())
```

### 4.3.6 — Generate the high-confidence subset
The script creates `data_clean/jrf_high_confidence.csv` containing only high-evidence entries.

```python
hc = pd.read_csv('../data_clean/jrf_high_confidence.csv')
print(f"High confidence: {len(hc)} out of {len(df)} total ({100*len(hc)/len(df):.0f}%)")
```

Target: ≥30% high confidence. If lower, consider relaxing evidence rules or adding more structural evidence.

## 4.4 — Manual Curation Pass (Critical!)

### 4.4.1 — Spot-check 20 random high-confidence entries
For each:
- [ ] Open UniProt page — is it really a capsid protein?
- [ ] Is the architecture class (SJR/DJR) correct?
- [ ] Is the T-number reasonable for this family?
- [ ] Is the host category correct?

### 4.4.2 — Spot-check 10 random low-confidence entries
For each:
- [ ] Why is it low confidence? (missing annotation? short fragment?)
- [ ] Should it be upgraded or removed?

### 4.4.3 — Look for systematic errors
```python
# Check for biologically impossible combinations:
# DJR + ssRNA should be very rare/absent
odd = df[(df['architecture_class']=='DJR') & (df['genome_type'].isin(['ssRNA+','ssRNA-']))]
print(f"DJR + ssRNA: {len(odd)} (should be ~0)")
print(odd[['organism','protein_name','family','genome_type']].to_string())
```

### 4.4.4 — Fix any errors found
Edit the lookup tables in `phase4_annotation.py`, re-run, verify fixes.

---

# ═══════════════════════════════════════════════════════════════════
# PHASE 5 — AGUILAR-STYLE STRUCTURAL EVOLUTION ANALYSIS
# ═══════════════════════════════════════════════════════════════════

**Goal:** Structure-based comparisons, domain co-occurrence network, evolutionary transition inference.

## 5.1 — Select Representative Structure Panel

### 5.1.1 — Define selection criteria
You want ~15–25 structures representing the diversity of JRF capsid proteins:
- At least 2 per genome type (ssDNA, ssRNA+, dsRNA, dsDNA)
- At least 3 SJR MCPs and 3 DJR MCPs
- At least 1 non-capsid JRF protein
- At least 1 archaeal virus
- At least 1 bacterial virus
- Maximize family diversity (don't pick 5 parvoviruses)
- Prefer high-resolution structures (≤ 3.5 Å)

### 5.1.2 — Pick structures from your high-confidence set
```python
hc = pd.read_csv('data_clean/jrf_high_confidence.csv')
# or from your seed set (guaranteed to have PDBs):
seeds = pd.read_csv('data_raw/jrf_seed_set.csv')
panel = seeds[seeds['capsid_role']=='MCP'][['virus_abbrev','primary_pdb','architecture_class','genome_type','family']]
print(panel.to_string())
```

### 5.1.3 — Verify the panel in `phase5_structural_analysis.py`
Check the `REPRESENTATIVE_STRUCTURES` dict. Update it to match your curated panel. Each entry needs:
```python
"label": {"pdb": "XXXX", "chain": "A", "architecture": "SJR|DJR", "family": "Xxx"}
```

### 5.1.4 — Check chain IDs
For each PDB code, verify the correct chain:
```bash
# Quick check via PDB API:
curl -s "https://data.rcsb.org/rest/v1/core/entry/1LP3" | python -m json.tool | grep -A5 "polymer_entities"
```
Or check on the RCSB website: Structure → Entity → note the chain letter.

## 5.2 — Structural Comparison: Option A — Simulated (Quick Start)

If you want to proceed without installing TM-align:

### 5.2.1 — Run with simulated TM-scores
```bash
python phase5_structural_analysis.py
```

This generates biologically plausible TM-scores using heuristics:
- Same architecture (SJR-SJR) → TM-score ~0.4–0.6
- Same family → TM-score ~0.5–0.8
- Cross-architecture (SJR-DJR) → TM-score ~0.2–0.4
- With random noise

**Use this for:** prototyping figures and pipeline testing. Replace with real scores later.

### 5.2.2 — Check outputs
```bash
ls ../analyses/structural_similarity_matrix.csv
ls ../analyses/structure_clustering.json
ls ../analyses/pfam_cooccurrence_network.json
ls ../figures/structural_similarity_heatmap.png
ls ../figures/structure_dendrogram.png
```

## 5.3 — Structural Comparison: Option B — Real TM-align (Recommended)

### 5.3.1 — Install TM-align
```bash
# Option 1: Download binary
wget https://zhanggroup.org/TM-align/TMalign -O ~/bin/TMalign
chmod +x ~/bin/TMalign
export PATH=$PATH:~/bin

# Option 2: Install via conda
conda install -c bioconda tmalign

# Verify:
TMalign -h
```

### 5.3.2 — Install US-align (Alternative/Enhancement)
US-align is the updated version:
```bash
wget https://zhanggroup.org/US-align/bin/module/USalign -O ~/bin/USalign
chmod +x ~/bin/USalign
```

### 5.3.3 — Run real structural comparisons
```bash
python phase5_structural_analysis.py --use-tmalign
```

**This will:**
1. Download PDB files for each representative from RCSB
2. Extract the specified chain
3. Run all pairwise TM-align comparisons (N*(N-1)/2 pairs)
4. Parse TM-scores
5. Build the real similarity matrix

**Expected time:** 5–30 minutes depending on panel size and download speed.

### 5.3.4 — Troubleshooting real TM-align
- **PDB download fails:** Some older codes may not be on RCSB. Try PDBe mirror: `https://www.ebi.ac.uk/pdbe/entry-files/download/pdbXXXX.ent`
- **Chain extraction fails:** Chain ID might differ between PDB and mmCIF format. Check manually.
- **TMalign returns 0:** Structures are too different. This is a valid result (TM-score ~0.15 = random).
- **Cryo-EM structures (mmCIF only):** May need to convert to PDB format first using BioPython or `gemmi`.

## 5.4 — Alternative/Enhanced: Foldseek for Fast Structure Search

### 5.4.1 — Install Foldseek
```bash
conda install -c conda-forge -c bioconda foldseek
```

### 5.4.2 — Run all-vs-all comparison
```bash
# Create a structure database from your panel PDBs
foldseek createdb pdb_files/ structDB
foldseek search structDB structDB resultDB tmp --exhaustive-search 1
foldseek convertalis structDB structDB resultDB results.tsv --format-output "query,target,fident,alnlen,mismatch,gapopen,qstart,qend,tstart,tend,evalue,bits,alntmscore"
```

### 5.4.3 — Parse Foldseek output into TM-score matrix
```python
import pandas as pd
import numpy as np

results = pd.read_csv('results.tsv', sep='\t', 
    names=['query','target','fident','alnlen','mismatch','gapopen',
           'qstart','qend','tstart','tend','evalue','bits','tmscore'])

# Pivot to square matrix
labels = sorted(set(results['query']) | set(results['target']))
matrix = pd.DataFrame(1.0, index=labels, columns=labels)
for _, row in results.iterrows():
    matrix.loc[row['query'], row['target']] = row['tmscore']
    matrix.loc[row['target'], row['query']] = row['tmscore']
```

## 5.5 — PFAM Co-occurrence Network

### 5.5.1 — Understand the concept
Nodes = PFAM domains. Edge between A and B if a single protein contains both domains. Weight = number of proteins with that combination.

### 5.5.2 — Why the current network is empty
The simulated data has only one PFAM per protein per family. To get real co-occurrence, you need proteins with **multiple PFAM annotations** — which requires fetching full domain architecture from InterPro.

### 5.5.3 — Fetch multi-domain architecture for your proteins
For each protein in the high-confidence set:
```python
import requests

def get_protein_domains(uniprot_id):
    """Get all PFAM domains for a protein from InterPro."""
    url = f"https://www.ebi.ac.uk/interpro/api/entry/pfam/protein/uniprot/{uniprot_id}?format=json"
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        domains = []
        for entry in data.get('results', []):
            domains.append({
                'pfam_id': entry['metadata']['accession'],
                'pfam_name': entry['metadata']['name'],
                'type': entry['metadata']['type']
            })
        return domains
    return []
```

### 5.5.4 — Build the co-occurrence matrix
```python
from collections import defaultdict
import itertools

cooccurrence = defaultdict(int)
for protein in proteins:
    domains = get_protein_domains(protein['uniprot_id'])
    pfam_ids = [d['pfam_id'] for d in domains]
    for a, b in itertools.combinations(sorted(pfam_ids), 2):
        cooccurrence[(a, b)] += 1
```

### 5.5.5 — Visualize with NetworkX
```python
import networkx as nx
G = nx.Graph()
for (a, b), weight in cooccurrence.items():
    if weight >= 2:  # minimum 2 proteins with this pair
        G.add_edge(a, b, weight=weight)
```

### 5.5.6 — Interpret the network
Look for:
- JRF capsid domains (SJR PFAM) co-occurring with protease, helicase, or RNA-dependent RNA polymerase domains
- DJR MCPs co-occurring with packaging ATPase domains
- Hub domains that appear in many different viruses
- Unexpected co-occurrences suggesting horizontal transfer or convergent evolution

## 5.6 — Structural Clustering and Tree

### 5.6.1 — Hierarchical clustering (already in Phase 5 script)
The script uses `scipy.cluster.hierarchy` with average linkage on the TM-score distance matrix.

### 5.6.2 — Review the dendrogram
Open `figures/structure_dendrogram.png`. Check:
- [ ] Do SJR proteins cluster together?
- [ ] Do DJR proteins cluster together?
- [ ] Are there any unexpected placements? (If so, investigate — could be real biology or an error)

### 5.6.3 — Define structural clusters
Use two distance thresholds:
- **Tight (TM-distance < 0.3):** Near-identical fold topology → same structural superfamily
- **Loose (TM-distance < 0.5):** Detectable structural similarity → same fold lineage

Record cluster memberships in `analyses/structure_clustering.json`.

### 5.6.4 — Make a phylogenetic-style structure tree (optional upgrade)
```bash
# Convert TM-score matrix to PHYLIP distance format
# Run neighbour-joining in MEGA, PHYLIP, or ete3
# Visualize with iTOL or ete3
```

## 5.7 — Evolutionary Transition Inference

### 5.7.1 — Define the transitions you want to test
Based on Aguilar et al. and your papers:

| Transition | Evidence Type | Key Comparison |
|-----------|---------------|----------------|
| SJR → DJR (gene duplication) | Structural: DJR N-half vs C-half vs SJR | TM-align DJR halves individually to SJR MCPs |
| DJR vertical inheritance (bacteria → eukaryotes) | Structural: DJR MCPs across hosts cluster together | Clustering pattern in dendrogram |
| SJR → movement protein (neofunctionalization) | Structural: 30K MP fold overlaps SJR capsid fold | TM-score of 1VIM vs SJR MCPs |
| T-number expansion (loop insertions) | Structural: larger T → more insertions in loops | Map loop lengths onto structural tree |
| SJR ssRNA ↔ ssDNA relationship | Structural: cross–genome-type SJR similarity | TM-scores between ssRNA and ssDNA SJRs |

### 5.7.2 — For SJR→DJR: Split DJR structures
```python
# For each DJR MCP structure, extract:
# - N-terminal JR domain (roughly first half)
# - C-terminal JR domain (roughly second half)
# Run TM-align of each half against SJR representatives
```
This is the strongest evidence for the duplication hypothesis.

### 5.7.3 — Record all transitions in structured JSON
```json
{
  "transition_id": "SJR_to_DJR",
  "description": "Gene duplication of SJR to form DJR",
  "evidence": [
    {"type": "structural", "detail": "DJR N-half TM-score to SJR = 0.45"},
    {"type": "literature", "detail": "Krupovic & Bamford 2008"}
  ],
  "support_level": "high",
  "direction": "SJR → DJR",
  "taxa_involved": ["Tectiviridae (DJR) ← unknown SJR ancestor"]
}
```

### 5.7.4 — Build the evolutionary schematic
Combine:
- Structure clustering (which folds are related)
- Domain co-occurrence (which accessory domains co-evolve)
- T-number correlations (fold complexity vs capsid size)
- Literature evidence

Output: A diagram showing the major evolutionary pathways within the JRF lineage.

---

# ═══════════════════════════════════════════════════════════════════
# PHASE 6 — VISUALIZATION & FINAL SYNTHESIS
# ═══════════════════════════════════════════════════════════════════

**Goal:** Publication-quality figures, summary tables, and narrative.

## 6.1 — Summary Tables

### 6.1.1 — Family overview table
Run Phase 6:
```bash
python phase6_visualization.py
```
Check `analyses/summary_family_overview.csv`. Should show for each family:
- Count of proteins
- Architecture class(es) present
- T-number(s)
- Number with structures
- Representative PDB

### 6.1.2 — Architecture summary table
Check `analyses/summary_architecture.csv`. Should show per architecture class:
- Count
- Families represented
- Genome types
- T-number range

### 6.1.3 — Genome × Architecture matrix
Check `analyses/genome_architecture_matrix.csv`. A crosstab showing how many proteins per genome type per architecture class.

## 6.2 — Core Figures (McKenna-Style)

### 6.2.1 — Architecture distribution pie chart
`figures/architecture_distribution.png`
- SJR, DJR, hybrid, etc. proportions
- Does SJR dominate? (Expected: yes, by count)

### 6.2.2 — Genome type bar chart
`figures/genome_type_distribution.png`
- ssRNA+ should have most SJR, dsDNA should have most DJR

### 6.2.3 — T-number distribution
`figures/t_number_distribution.png`
- T=3 and pseudo-T=3 should dominate SJR
- Higher T-numbers for DJR

### 6.2.4 — Genome × Architecture heatmap
`figures/genome_architecture_heatmap.png`
- This is the key "capsidomics coverage map"

### 6.2.5 — Top families bar chart
`figures/family_overview.png`
- Horizontal bars, color-coded by architecture

## 6.3 — Structural Figures (Aguilar-Style)

### 6.3.1 — Structural similarity heatmap
`figures/structural_similarity_heatmap.png`
- Reorder by clustering
- Should show clear SJR/DJR blocks

### 6.3.2 — Structure dendrogram
`figures/structure_dendrogram.png`
- Annotate with architecture class and genome type

### 6.3.3 — Evolutionary schematic
Replace the ASCII art in `figures/evolutionary_schematic.txt` with a proper figure:

**Option A — Manual in PowerPoint/Illustrator:**
Draw a schematic showing:
```
Ancestral JRF (SJR)
    ├── ssRNA+ capsids (Picorna, Noda, Tombus)
    ├── ssDNA capsids (Parvo, Circo, Gemini)
    ├── Gene duplication → DJR ancestor
    │       ├── PRD1/Tectiviridae
    │       ├── Adenoviridae
    │       └── NCLDVs (Phycodna, Asfar, Irido, Mimi)
    ├── Neofunctionalization → Movement proteins (30K)
    └── dsRNA capsids (Birna)
```

**Option B — Programmatic (Python/matplotlib):**
Use networkx or graphviz to draw a directed graph of evolutionary relationships.

## 6.4 — Optional: PFAM Co-occurrence Network Figure

### 6.4.1 — If you built a real co-occurrence network (Phase 5.5):
```python
import networkx as nx
import matplotlib.pyplot as plt

G = nx.read_gml('analyses/pfam_cooccurrence_network.gml')
pos = nx.spring_layout(G, k=2)
nx.draw(G, pos, with_labels=True, node_size=500, font_size=8)
plt.savefig('figures/pfam_network.png', dpi=300)
```

## 6.5 — Generate Final Summary Statistics

### 6.5.1 — Run the summary generator
Already done by Phase 6. Check `analyses/final_summary_statistics.json`.

### 6.5.2 — Key numbers to report
Record these for your paper/presentation:
- Total JRF proteins in atlas: ___
- High-confidence capsid subset: ___
- Families covered: ___
- Unique virus species: ___
- SJR : DJR ratio: ___
- Proteins with experimental structure: ___
- Proteins with AlphaFold model: ___
- Genome types represented: ___
- Host categories represented: ___

## 6.6 — Final Quality Assurance

### 6.6.1 — Cross-check master CSV against literature
Open `data_clean/jrf_capsidomics_master.csv` in Excel. Compare against:
- McKenna/Mietzsch ssDNA capsidomics paper tables → are all their viruses represented?
- Aguilar et al. structural panel → are all their representative structures in your panel?

### 6.6.2 — Check for known gaps
Known JRF families that should be represented:
- [ ] Parvoviridae (ssDNA, SJR)
- [ ] Circoviridae (ssDNA, SJR)
- [ ] Geminiviridae (ssDNA, SJR)
- [ ] Microviridae (ssDNA, SJR, phage)
- [ ] Picornaviridae (ssRNA+, SJR)
- [ ] Nodaviridae (ssRNA+, SJR)
- [ ] Tombusviridae (ssRNA+, SJR)
- [ ] Bromoviridae (ssRNA+, SJR)
- [ ] Birnaviridae (dsRNA, SJR)
- [ ] Tectiviridae (dsDNA, DJR)
- [ ] Adenoviridae (dsDNA, DJR)
- [ ] Phycodnaviridae (dsDNA, DJR)
- [ ] Asfarviridae (dsDNA, DJR)
- [ ] Iridoviridae (dsDNA, DJR)
- [ ] Mimiviridae (dsDNA, DJR)
- [ ] Poxviridae (dsDNA, DJR scaffold)
- [ ] Turriviridae (dsDNA, DJR, archaeal)
- [ ] Corticoviridae (dsDNA, DJR)
- [ ] Leviviridae (ssRNA+, SJR, phage)

### 6.6.3 — Completeness assessment
```python
import pandas as pd
df = pd.read_csv('data_clean/jrf_capsidomics_master.csv')
expected_families = [
    'Parvoviridae','Circoviridae','Geminiviridae','Microviridae',
    'Picornaviridae','Nodaviridae','Tombusviridae','Bromoviridae',
    'Birnaviridae','Tectiviridae','Adenoviridae','Phycodnaviridae',
    'Asfarviridae','Iridoviridae','Poxviridae','Turriviridae'
]
present = df['family'].unique()
for f in expected_families:
    status = "✓" if f in present else "✗ MISSING"
    print(f"  {status} {f}")
```

---

# ═══════════════════════════════════════════════════════════════════
# APPENDIX A — COMMON COMMANDS CHEAT SHEET
# ═══════════════════════════════════════════════════════════════════

```bash
# === Run full pipeline (demo mode — simulated data) ===
python run_pipeline.py

# === Run full pipeline (real data — API calls) ===
python run_pipeline.py --full

# === Run individual phases ===
cd scripts/
python phase1_seed_set.py
python phase2_pfam_mapping.py
python phase3_expansion.py --use-api
python phase4_annotation.py --lookup-structures
python phase5_structural_analysis.py --use-tmalign
python phase6_visualization.py

# === Quick data inspection ===
python -c "import pandas as pd; df=pd.read_csv('data_raw/jrf_seed_set.csv'); print(len(df), 'seeds')"
python -c "import pandas as pd; df=pd.read_csv('data_raw/jrf_pfam_master.csv'); print(len(df), 'PFAMs')"
python -c "import pandas as pd; df=pd.read_csv('data_clean/jrf_all_hits_clean.csv'); print(len(df), 'clean hits')"
python -c "import pandas as pd; df=pd.read_csv('data_clean/jrf_capsidomics_master.csv'); print(len(df), 'annotated')"
python -c "import pandas as pd; df=pd.read_csv('data_clean/jrf_high_confidence.csv'); print(len(df), 'high confidence')"

# === UniProt API test ===
curl -s "https://rest.uniprot.org/uniprotkb/P03135?format=json" | python -m json.tool | head -30

# === InterPro PFAM membership count ===
curl -s "https://www.ebi.ac.uk/interpro/api/entry/pfam/PF00740/protein/uniprot/?page_size=1" | python -m json.tool | grep count

# === PDB structure check ===
curl -s "https://data.rcsb.org/rest/v1/core/entry/1LP3" | python -m json.tool | grep -i resolution
```

---

# ═══════════════════════════════════════════════════════════════════
# APPENDIX B — DECISION LOG TEMPLATE
# ═══════════════════════════════════════════════════════════════════

Keep a running log of every non-obvious decision:

```markdown
## Decision Log

### D001 — Scope of "JRF-derived non-capsid"
**Date:** ___
**Decision:** Include movement proteins and spike proteins. Exclude purely cellular nucleoplasmin.
**Reason:** Movement proteins have clear viral origin; nucleoplasmin is too divergent to confidently classify.

### D002 — Minimum protein length for inclusion
**Date:** ___
**Decision:** 80 aa minimum (JRF core is ~150 aa but fragments start at ~80)
**Reason:** Below 80 aa, domain assignment is unreliable.

### D003 — Strain deduplication strategy
**Date:** ___
**Decision:** Keep one representative per species per serotype. Cluster at 95% identity.
**Reason:** Avoid AAV serotype inflation (AAV1-AAV13 would dominate the dataset).

### D004 — [Add yours]
```

---

# ═══════════════════════════════════════════════════════════════════
# APPENDIX C — TIMELINE & MILESTONES
# ═══════════════════════════════════════════════════════════════════

| Week | Phase | Deliverable | Verification |
|------|-------|-------------|--------------|
| 1 | 0 + 1 | Environment setup, literature reading, seed set complete | `jrf_seed_set.csv` with 30–50 entries, all PDBs verified |
| 2 | 2 + 3 | PFAM master complete, expansion run with real APIs | `jrf_all_hits_clean.csv` with 200+ real entries |
| 3 | 4 | Capsidomics annotation complete, high-confidence set defined | `jrf_capsidomics_master.csv` fully annotated, <20% unknown fields |
| 4 | 5 | Structural comparisons (TM-align or Foldseek), domain network built | `structural_similarity_matrix.csv` with real TM-scores |
| 5 | 5 cont. | Evolutionary transitions documented | `evolutionary_transitions.json` with evidence citations |
| 6 | 6 | All figures generated, summary tables complete | All PNGs in `figures/`, summary CSVs in `analyses/` |
| 7–8 | Polish | Manual curation pass, narrative writing, PI review | Draft results section or lab meeting presentation |

---

# ═══════════════════════════════════════════════════════════════════
# APPENDIX D — WHAT TO DO IF APIs FAIL / DATA IS INCOMPLETE
# ═══════════════════════════════════════════════════════════════════

## Problem: InterPro / UniProt API returns errors

**Solution 1:** Check status page: https://www.ebi.ac.uk/interpro/about/
**Solution 2:** Add longer delays (increase `rate_limit` to 2.0 seconds)
**Solution 3:** Download bulk data files instead:
- InterPro: https://www.ebi.ac.uk/interpro/download/
- UniProt: https://www.uniprot.org/downloads

## Problem: PFAM has been deprecated / merged into InterPro

As of ~2023, PFAM has been integrated into InterPro. The PFAM IDs still work as InterPro member database entries. Use the InterPro API with PFAM accessions:
```
https://www.ebi.ac.uk/interpro/api/entry/pfam/PF00740/
```

## Problem: Too many hits from expansion (>10,000)

**Strategy:**
1. Add stricter taxonomy filter (e.g., only RefSeq reference proteomes)
2. Cluster at 90% sequence identity using CD-HIT
3. Take only reviewed (Swiss-Prot) entries as first pass

```bash
# Install CD-HIT
conda install -c bioconda cd-hit
# Cluster at 90%
cd-hit -i all_sequences.fasta -o clustered_90.fasta -c 0.9 -n 5
```

## Problem: No PDB structure exists for a protein

**Fallback hierarchy:**
1. Check AlphaFold DB: https://alphafold.ebi.ac.uk/entry/UNIPROTID
2. Check ESMFold: https://esmatlas.com/
3. Run ColabFold for the JRF domain only
4. Record as `structure_source=none` and note in evidence level

## Problem: Novel/unclassified viruses in expansion

Keep them! Label `family=Unclassified` and annotate what you can. These are interesting for evolutionary analysis (potential intermediates).

---

# ═══════════════════════════════════════════════════════════════════
# APPENDIX E — EXTENDING THE ATLAS (FUTURE WORK)
# ═══════════════════════════════════════════════════════════════════

Once the core atlas is built, natural extensions include:

1. **AlphaFold-scale structural comparison:** Use Foldseek to compare all AlphaFold models of JRF proteins (not just experimentally solved)
2. **Sequence phylogeny vs. structure tree:** Compare PFAM HMM-based sequence tree with structural clustering — do they agree?
3. **Interface analysis:** Following the T=3 interface diversity paper, analyze capsid protein–protein interfaces across families
4. **Metagenomics integration:** Pull JRF hits from IMG/VR or MGnify virus databases
5. **Capsid engineering annotation:** Add columns for known engineered variants (AAV display/targeting, CCMV nanocages)
6. **Procapsid / maturation data:** Following Aguilar's assembly logic, annotate which proteins have known procapsid states

---

*Document generated for the JRF Capsidomics Atlas project.*
*Last updated: 2026-03-03*
