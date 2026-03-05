# How to Build a Literature-Verified JRF Seed Set of 50 Proteins

---

## Overview

Build the seed set in three stages:

1. Decide which viral families to represent
2. Find the canonical structural paper for each
3. Extract and verify every field from that paper and its associated database entries

Nothing goes into the CSV unless you can cite the exact paper it came from.

---

## Stage 1 — Define your 50 slots by family

Allocate slots across JRF lineages before you look up anything. This prevents bias toward well-studied families.

| Lineage | Families to cover | Slots |
|---|---|---|
| SJR ssDNA | Parvoviridae, Circoviridae, Anelloviridae, Geminiviridae, Microviridae, Smacoviridae | 10 |
| SJR ssRNA+ | Picornaviridae, Nodaviridae, Tombusviridae, Bromoviridae, Sobemoviridae, Tymoviridae, Leviviridae | 10 |
| SJR ssRNA- | Qinviridae (if structural data exists) | 1 |
| SJR dsRNA | Birnaviridae, Partitiviridae | 3 |
| DJR dsDNA (bacteriophage) | Tectiviridae, Corticoviridae | 4 |
| DJR dsDNA (eukaryotic) | Adenoviridae, Phycodnaviridae, Asfarviridae, Iridoviridae, Mimiviridae | 8 |
| DJR dsDNA (archaeal) | Turriviridae, Portogloboviridae | 3 |
| JRF-derived non-capsid | Movement proteins (30K family), turret/spike proteins | 4 |
| Unclassified / novel lineages | Emerging structural hits from recent cryo-EM papers | 7 |

Adjust slots as you go — if a family has no solved structure yet, replace it. The goal is phylogenetic and functional breadth, not filling every slot for its own sake.

---

## Stage 2 — Find the primary structure paper for each slot

For each family in your allocation, find the **original structure determination paper** — not a review, not a database entry, but the paper where the structure was first published or the most authoritative high-resolution revision.

### Step 2a — Search PubMed

Go to https://pubmed.ncbi.nlm.nih.gov and search:

- `[family name] capsid protein crystal structure`
- `[family name] cryo-EM capsid`
- `[virus name] major capsid protein structure`

Look specifically for papers that report:

- X-ray crystallography or cryo-EM
- Resolution better than 4 Å (ideally ≤3.5 Å)
- A deposited PDB entry

### Step 2b — Check the RCSB PDB directly

Go to https://www.rcsb.org and search the virus family name or virus name. Filter by:

- Polymer type: Protein
- Experimental method: X-RAY DIFFRACTION or ELECTRON MICROSCOPY

For each hit, open the structure page and read the **Primary Citation** field — this is the paper you want.

### Step 2c — Use ViPER database for icosahedral viruses

Go to https://viperdb.org — this database only contains validated icosahedral capsid structures. Every entry links directly to the PDB entry and the primary paper. This is the most reliable starting point for icosahedral entries.

### Step 2d — For giant viruses and NCLDVs

Search the Giant Virus Database (https://gvdb.biomedicale.parisdescartes.fr) or search PubMed for:

- `NCLDV major capsid protein structure`
- `Nucleocytoviricota cryo-EM`

### Step 2e — For novel/recent entries

Search bioRxiv and the most recent issues of PNAS, Nature, eLife, PLOS Pathogens, Journal of Virology, and Acta Crystallographica D (2018–2026) for new JRF structures.

---

## Stage 3 — Extract every field from the paper and databases

For each of your 50 proteins, open the paper and the PDB/UniProt entry side by side and fill in each field from primary sources only.

---

### Field 1 — `virus_name`

- Take the **full, formal species name** from the ICTV Master Species List: https://ictv.global/msl
- Do not use abbreviations or colloquial names here
- Check the current ICTV release — family names and species names change; use the 2024 or 2025 release

---

### Field 2 — `family` and `realm/order`

- Go to https://ictv.global/taxonomy and navigate to the species
- Record the full lineage: Realm → Kingdom → Phylum → Class → Order → Family → Genus → Species
- Note the realm explicitly — this is critical for the evolutionary schematic later (Baltimore classification alone is insufficient)

---

### Field 3 — `genome_type`

- Read from the ICTV entry, not the paper (papers sometimes use informal descriptions)
- Use controlled vocabulary only: `ssDNA`, `dsDNA`, `ssRNA+`, `ssRNA-`, `dsRNA`
- For ambisense genomes: `ssRNA_ambisense`

---

### Field 4 — `host_category`

- Read from the paper's introduction or from the ICTV entry
- Use: `Bacteria`, `Archaea`, `Eukaryota_Animal`, `Eukaryota_Plant`, `Eukaryota_Fungi`, `Eukaryota_Protist`
- Do not guess from virus name alone — some plant-sounding viruses infect insects as secondary hosts

---

### Field 5 — `protein_name`

- Use the name from the **primary structure paper**, not the database
- Include the functional prefix: VP1, VP2, MCP, coat protein, hexon, P3, etc.
- Record the molecular weight if given in the paper

---

### Field 6 — `pdb_id`

- Go to https://www.rcsb.org and look up the structure from the primary paper
- Take the 4-character PDB accession code
- If multiple structures exist for the same protein, take the highest-resolution one — record the others as `alt_pdb_ids`
- Open the PDB page and confirm: (a) the protein name matches, (b) the organism name matches, (c) the experimental method is correct

---

### Field 7 — `architecture_class`

This requires reading the paper's structural analysis section, not just the abstract. Look for:

**SJR (Single Jelly-Roll):** The paper describes an 8-stranded antiparallel beta-barrel (strands named BIDG and CHEF). Often described as "jelly-roll fold" or "β-barrel". One jelly-roll domain per subunit.

**DJR (Double Jelly-Roll):** Two jelly-roll domains in a single polypeptide chain. The paper will explicitly describe a "double jelly-roll" or show two β-barrels in the topology diagram. MCP is typically 40–60 kDa.

**JRF_derived:** The protein has a JRF-like fold but is not a structural capsid component (movement proteins, spike proteins, turret proteins). The paper will show structural homology to capsid proteins via DALI or SSM search.

If the paper does not explicitly discuss fold topology, look at the figure showing the ribbon diagram — count the beta-strands in the barrel.

---

### Field 8 — `t_number`

- Read directly from the paper — it will be stated in the results or methods section as "T=3", "pseudo-T=3", "T=13", etc.
- For asymmetric or non-icosahedral virions: write `NA`
- For particles with disputed T-numbers, write the value the paper reports and add a note

---

### Field 9 — `capsid_role`

- Read from the paper's description of protein function
- Use controlled vocabulary:
  - `MCP` — major capsid protein contributing most of the capsid surface
  - `minor` — present in small numbers at specific positions
  - `spike` — protruding structure at vertices
  - `cement` — holds facets or subunits together
  - `turret` — vertex turret structure
  - `scaffold` — needed for assembly, may be absent from mature virion
  - `movement` — non-capsid, cell-to-cell movement function

---

### Field 10 — `uniprot_id`

- Go to https://www.uniprot.org and search by virus name + protein name
- **Use Swiss-Prot (reviewed) entries only** — look for the gold star/reviewed badge
- Open the entry and verify: the organism must match your virus exactly, not a different strain
- Record the 6-character accession (e.g., P03135), not the entry name

---

### Field 11 — `reference_pmid`

- Go to https://pubmed.ncbi.nlm.nih.gov
- Search the exact paper title or first author + year
- Record the PMID number (shown in the URL or the "PMID:" field)
- Do not use a review paper as the primary reference — use the original structure paper

---

### Field 12 — `notes`

Write 1–2 sentences from the paper that justify inclusion: why this protein is a confirmed JRF protein, any unusual features, and the resolution of the structure.

---

## Stage 4 — Cross-verify each entry

After filling in all fields for a protein, run these three checks:

### Check A — PDB cross-reference

Open the PDB entry. Does the organism name in PDB match your `virus_name`? Does the chain you selected contain the protein you think it does? Read the "Macromolecules" table in the PDB entry.

### Check B — UniProt cross-reference

Open the UniProt entry. Does the sequence length match what the paper reports for the MCP? Is there a "3D Structure" section listing the same PDB accession?

### Check C — PMID cross-reference

Open the PubMed entry. Does the publication year, journal, and authors match what is cited in the PDB entry's Primary Citation? PDB and PubMed must agree on the same paper.

If any of the three checks fail, go back to the paper and re-derive the field.

---

## Stage 5 — Assemble the CSV manually before coding

Before touching the script, build the table in a spreadsheet (Excel or Google Sheets) with one row per protein and one column per field. This lets you:

- Spot missing values before they become bugs
- Sort by family to check for duplicate entries
- Review all 50 rows at once for consistency in controlled vocabulary

Only once the spreadsheet is complete and cross-verified should you transfer it into the `SEED_PROTEINS` list in the script — by replacing the existing hardcoded list with your verified entries.

---

## Key sources summary

| What you need | Where to get it |
|---|---|
| Authoritative virus taxonomy | https://ictv.global/taxonomy |
| Canonical icosahedral capsid structures | https://viperdb.org |
| PDB structure + primary citation | https://www.rcsb.org |
| Reviewed protein sequences | https://www.uniprot.org (Swiss-Prot only) |
| Paper PMIDs and abstracts | https://pubmed.ncbi.nlm.nih.gov |
| Giant virus structures | https://gvdb.biomedicale.parisdescartes.fr |
| Recent novel structures | PubMed 2020–2026, filtered to structure papers |
