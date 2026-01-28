# JRF Capsidomics Atlas - Schema Definitions

## Operational Definitions

This document provides precise definitions for classification terms used throughout the JRF Capsidomics Atlas.

---

## 1. Jelly-Roll Fold (JRF) Classification

### 1.1 Single Jelly-Roll (SJR)
**Definition:** A protein containing ONE jelly-roll domain (8-stranded antiparallel β-barrel with topology B-I-D-G and C-H-E-F sheets).

**Characteristics:**
- Typically 150-300 amino acids for the core domain
- Orientation: Usually **tangential** to capsid surface (sheets parallel to surface)
- Found in: ssRNA viruses, ssDNA viruses (parvoviruses, circoviruses)
- Example structures: Picornavirus VP1-3, Parvovirus VP

**Canonical PFAM domains:**
- PF00729 (Viral_coat, Picornavirus capsid protein)
- PF00740 (Parvo_coat, Parvovirus coat protein)
- PF02227 (Viral_caps, Plant virus capsid protein)

### 1.2 Double Jelly-Roll (DJR)
**Definition:** A protein containing TWO tandemly-fused jelly-roll domains forming a pseudohexameric tower.

**Characteristics:**
- Typically 400-700 amino acids
- Orientation: **Perpendicular** to capsid surface (β-barrels point outward)
- Found in: PRD1-adenovirus-NCLDVs lineage, archaeal viruses
- Evidence of ancient gene duplication from SJR ancestor

**Canonical PFAM domains:**
- PF09018 (Adeno_hexon_N, Adenovirus hexon N-terminal)
- PF00608 (Adeno_hexon, Adenovirus hexon protein)
- PF04451 (DUF557, PRD1-type DJR MCP)

### 1.3 JRF-Derived (Non-Capsid)
**Definition:** Proteins with detectable JRF fold homology but functioning outside the capsid shell.

**Categories:**
- **Movement proteins:** Plant virus 30K superfamily (cell-to-cell transport)
- **Spike/turret proteins:** Vertex decorations, receptor binding
- **Cement proteins:** Inter-capsomer stabilization
- **Nuclear factors:** Nucleoplasmin-like assembly chaperones
- **Matrix proteins:** Membrane-associated functions

---

## 2. Evidence Level Classification

### 2.1 High Confidence
All of the following must be true:
- [ ] Annotated as capsid/coat/MCP in UniProt OR >3 literature references
- [ ] Matched to a "capsid-type" JRF PFAM domain
- [ ] Domain boundaries reasonable (not truncated fragments)
- [ ] Experimental structure available (PDB) or high-quality AlphaFold model

### 2.2 Medium Confidence
At least two of:
- [ ] Annotated as capsid/coat in UniProt
- [ ] Matched to JRF PFAM domain
- [ ] Genomic neighborhood consistent with capsid gene
- [ ] Literature evidence exists

### 2.3 Low Confidence
- [ ] Sequence similarity to JRF only (no functional annotation)
- [ ] Fragmentary sequences
- [ ] Ambiguous domain matches

---

## 3. Capsid Architecture Fields

### 3.1 Capsid Role
| Value | Definition |
|-------|------------|
| `MCP` | Major Capsid Protein - primary structural component |
| `minor` | Minor capsid protein - less abundant structural component |
| `spike` | Vertex spike or fiber protein |
| `turret` | Turret protein at vertices |
| `cement` | Cement/glue protein stabilizing interfaces |
| `movement` | Cell-to-cell movement protein (plant viruses) |
| `matrix` | Matrix protein (membrane-associated) |
| `non-capsid` | JRF-containing but non-capsid function |
| `unknown` | Function not determined |

### 3.2 Architecture Class
| Value | Definition |
|-------|------------|
| `SJR` | Single jelly-roll domain |
| `DJR` | Double jelly-roll (tandem fusion) |
| `tandem_JRF` | Multiple JRF domains (>2) |
| `JRF_hybrid` | JRF + non-JRF domain architecture |
| `nucleoplasmin_like` | JRF-derived nucleoplasmin fold |
| `other` | Other JRF-related architecture |

### 3.3 T-Number (Triangulation Number)
| Value | Description | Copy Number (of one subunit type) |
|-------|-------------|-----------------------------------|
| `T=1` | Smallest icosahedral | 60 |
| `T=3` | Common in small RNA viruses | 180 |
| `pseudo-T=3` | Parvovirus-type (T=1 with 3 domains) | 60 |
| `T=7` | Medium-sized capsids | 420 |
| `T=13` | Adenovirus-type | 780 |
| `T=25` | Giant virus class | 1500 |
| `higher` | Very large capsids (T>25) | >1500 |
| `NA` | Non-icosahedral or unknown | - |

### 3.4 Virion Morphology
| Value | Description |
|-------|-------------|
| `icosahedral` | True icosahedral symmetry |
| `geminate` | Twinned icosahedra (geminiviruses) |
| `prolate` | Elongated icosahedron |
| `filamentous` | Filamentous/rod-shaped |
| `pleomorphic` | Variable shape |
| `enveloped` | Icosahedral core with envelope |
| `complex` | Complex morphology |

---

## 4. Genome Type Classification

| Value | Description | Example Families |
|-------|-------------|------------------|
| `ssDNA` | Single-stranded DNA | Parvoviridae, Circoviridae, Microviridae |
| `dsDNA` | Double-stranded DNA | Adenoviridae, NCLDVs, PRD1-like |
| `ssRNA+` | Positive-sense ssRNA | Picornaviridae, Nodaviridae, Tombusviridae |
| `ssRNA-` | Negative-sense ssRNA | Generally lacks JRF capsids |
| `dsRNA` | Double-stranded RNA | Reoviridae, Birnaviridae |

---

## 5. Host Category Classification

| Value | Subcategories |
|-------|---------------|
| `Bacteria` | Gram+, Gram-, Cyanobacteria |
| `Archaea` | Euryarchaeota, Crenarchaeota, TACK |
| `Eukaryota_Animal` | Vertebrates, Invertebrates |
| `Eukaryota_Plant` | Angiosperms, Gymnosperms, Algae |
| `Eukaryota_Fungi` | Yeasts, Filamentous fungi |
| `Eukaryota_Protist` | Protozoa, Amoebae |
| `Multiple` | Broad host range |

---

## 6. PFAM Classification for JRF

### 6.1 High-Confidence Capsid PFAMs (include in atlas)
```
PF00729  Viral_coat      Picornavirus capsid
PF00740  Parvo_coat      Parvovirus coat
PF02227  Viral_caps      Plant virus capsid
PF00729  Rhv             Rhinovirus capsid
PF08398  Circovirus_cap  Circovirus capsid
PF01141  Noda_capsid     Nodavirus capsid
```

### 6.2 JRF-Derived Non-Capsid PFAMs (track separately)
```
PF01107  30Kc            Movement protein superfamily
PF00927  Nucleoplasmin   Nucleoplasmin/nucleophosmin
```

### 6.3 DJR-Associated PFAMs
```
PF09018  Adeno_hexon_N   Adenovirus hexon N-terminal
PF00608  Adeno_hexon     Adenovirus hexon protein
PF04451  DUF557          PRD1-type DJR MCP
```

---

## 7. Quality Control Filters

### 7.1 Sequence Quality
- Minimum length: 100 aa (to exclude fragments)
- Maximum length: 2000 aa (exclude obvious misannotations)
- No internal stop codons
- Complete N- and C-termini preferred

### 7.2 Redundancy Handling
- Cluster at 90% identity to remove strain-level redundancy
- Keep one representative per cluster
- Prefer: PDB structure > SwissProt entry > TrEMBL entry

### 7.3 Taxonomic Filtering
- Include only virus taxonomy IDs
- Exclude: cellular organisms, plasmids, synthetic constructs
- Map to ICTV-approved taxonomy where possible

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-27 | Initial schema definitions |

