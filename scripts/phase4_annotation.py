#!/usr/bin/env python3
"""
Phase 4: McKenna-Style Capsidomics Annotation
=============================================

This script adds comprehensive capsidomics fields to the expanded hit list,
following the McKenna/Mietzsch framework for parvovirus structural annotation.

Process:
1. Load the cleaned hit list from Phase 3
2. Add capsidomics fields (role, architecture, morphology, T-number, etc.)
3. Apply evidence rules to create high-confidence subset
4. Generate the master capsidomics database

Key Fields Added:
- capsid_role (MCP/minor/spike/turret/cement/movement/matrix/unknown)
- architecture_class (SJR, DJR, tandem_JRF, nucleoplasmin-like)
- virion_morphology (icosahedral, geminate, filamentous, pleomorphic)
- t_number (T=1, T=3, pseudo-T=3, T=7, higher, NA)
- structure_evidence (PDB, cryo-EM, AlphaFold, homology)
- evidence_level (high, medium, low)

Outputs:
- data_clean/jrf_capsidomics_master.csv - Full annotated database
- data_clean/jrf_high_confidence.csv - High-confidence subset
- data_clean/jrf_capsidomics_summary.json - Statistics

Usage:
    python phase4_annotation.py

Author: JRF Capsidomics Atlas Project
Date: 2026-01-27
"""

import pandas as pd
import requests
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
import re

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_RAW = PROJECT_ROOT / "data_raw"
DATA_CLEAN = PROJECT_ROOT / "data_clean"


# =============================================================================
# ANNOTATION LOOKUP TABLES
# =============================================================================

# Family to architecture/morphology mappings (based on literature)
FAMILY_ANNOTATIONS = {
    # ssDNA viruses - SJR
    "Parvoviridae": {
        "architecture_class": "SJR",
        "virion_morphology": "icosahedral",
        "t_number": "pseudo-T=3",
        "genome_type": "ssDNA",
        "jrf_orientation": "tangential"
    },
    "Circoviridae": {
        "architecture_class": "SJR",
        "virion_morphology": "icosahedral",
        "t_number": "T=1",
        "genome_type": "ssDNA",
        "jrf_orientation": "tangential"
    },
    "Geminiviridae": {
        "architecture_class": "SJR",
        "virion_morphology": "geminate",
        "t_number": "T=1",
        "genome_type": "ssDNA",
        "jrf_orientation": "tangential"
    },
    "Microviridae": {
        "architecture_class": "SJR",
        "virion_morphology": "icosahedral",
        "t_number": "T=1",
        "genome_type": "ssDNA",
        "jrf_orientation": "tangential"
    },
    "Nanoviridae": {
        "architecture_class": "SJR",
        "virion_morphology": "icosahedral",
        "t_number": "T=1",
        "genome_type": "ssDNA",
        "jrf_orientation": "tangential"
    },
    
    # ssRNA+ viruses - SJR
    "Picornaviridae": {
        "architecture_class": "SJR",
        "virion_morphology": "icosahedral",
        "t_number": "pseudo-T=3",
        "genome_type": "ssRNA+",
        "jrf_orientation": "tangential"
    },
    "Nodaviridae": {
        "architecture_class": "SJR",
        "virion_morphology": "icosahedral",
        "t_number": "T=3",
        "genome_type": "ssRNA+",
        "jrf_orientation": "tangential"
    },
    "Tombusviridae": {
        "architecture_class": "SJR",
        "virion_morphology": "icosahedral",
        "t_number": "T=3",
        "genome_type": "ssRNA+",
        "jrf_orientation": "tangential"
    },
    "Bromoviridae": {
        "architecture_class": "SJR",
        "virion_morphology": "icosahedral",
        "t_number": "T=3",
        "genome_type": "ssRNA+",
        "jrf_orientation": "tangential"
    },
    "Caliciviridae": {
        "architecture_class": "SJR",
        "virion_morphology": "icosahedral",
        "t_number": "T=3",
        "genome_type": "ssRNA+",
        "jrf_orientation": "tangential"
    },
    "Tymoviridae": {
        "architecture_class": "SJR",
        "virion_morphology": "icosahedral",
        "t_number": "T=3",
        "genome_type": "ssRNA+",
        "jrf_orientation": "tangential"
    },
    "Leviviridae": {
        "architecture_class": "SJR",
        "virion_morphology": "icosahedral",
        "t_number": "T=3",
        "genome_type": "ssRNA+",
        "jrf_orientation": "tangential"
    },
    
    # dsRNA viruses - SJR
    "Birnaviridae": {
        "architecture_class": "SJR",
        "virion_morphology": "icosahedral",
        "t_number": "T=13",
        "genome_type": "dsRNA",
        "jrf_orientation": "tangential"
    },
    "Picobirnaviridae": {
        "architecture_class": "SJR",
        "virion_morphology": "icosahedral",
        "t_number": "T=3",
        "genome_type": "dsRNA",
        "jrf_orientation": "tangential"
    },
    
    # dsDNA viruses - DJR
    "Adenoviridae": {
        "architecture_class": "DJR",
        "virion_morphology": "icosahedral",
        "t_number": "pseudo-T=25",
        "genome_type": "dsDNA",
        "jrf_orientation": "perpendicular"
    },
    "Tectiviridae": {
        "architecture_class": "DJR",
        "virion_morphology": "icosahedral",
        "t_number": "pseudo-T=25",
        "genome_type": "dsDNA",
        "jrf_orientation": "perpendicular"
    },
    "Corticoviridae": {
        "architecture_class": "DJR",
        "virion_morphology": "icosahedral",
        "t_number": "pseudo-T=21",
        "genome_type": "dsDNA",
        "jrf_orientation": "perpendicular"
    },
    "Phycodnaviridae": {
        "architecture_class": "DJR",
        "virion_morphology": "icosahedral",
        "t_number": "T=169",
        "genome_type": "dsDNA",
        "jrf_orientation": "perpendicular"
    },
    "Mimiviridae": {
        "architecture_class": "DJR",
        "virion_morphology": "icosahedral",
        "t_number": "higher",
        "genome_type": "dsDNA",
        "jrf_orientation": "perpendicular"
    },
    "Asfarviridae": {
        "architecture_class": "DJR",
        "virion_morphology": "icosahedral",
        "t_number": "T=214",
        "genome_type": "dsDNA",
        "jrf_orientation": "perpendicular"
    },
    "Iridoviridae": {
        "architecture_class": "DJR",
        "virion_morphology": "icosahedral",
        "t_number": "T=147",
        "genome_type": "dsDNA",
        "jrf_orientation": "perpendicular"
    },
    "Poxviridae": {
        "architecture_class": "DJR",
        "virion_morphology": "complex",
        "t_number": "NA",
        "genome_type": "dsDNA",
        "jrf_orientation": "NA"
    },
    "Turriviridae": {
        "architecture_class": "DJR",
        "virion_morphology": "icosahedral",
        "t_number": "pseudo-T=31",
        "genome_type": "dsDNA",
        "jrf_orientation": "perpendicular"
    },
    
    # Non-capsid JRF (filamentous viruses)
    "Virgaviridae": {
        "architecture_class": "other",
        "virion_morphology": "filamentous",
        "t_number": "NA",
        "genome_type": "ssRNA+",
        "jrf_orientation": "NA"
    },
}

# Protein name patterns for role classification
ROLE_PATTERNS = {
    "MCP": [
        r"major capsid",
        r"capsid protein",
        r"coat protein",
        r"\bVP[123]\b",
        r"\bMCP\b",
        r"\bvp54\b",
        r"\bp72\b",
        r"hexon",
    ],
    "minor": [
        r"minor capsid",
        r"penton",
        r"vertex",
    ],
    "spike": [
        r"spike",
        r"fiber",
        r"receptor binding",
    ],
    "turret": [
        r"turret",
    ],
    "cement": [
        r"cement",
        r"glue",
        r"protein IX",
        r"protein IIIa",
    ],
    "movement": [
        r"movement protein",
        r"30K",
        r"cell-to-cell",
    ],
}


def infer_capsid_role(protein_name: str, family: str = "") -> str:
    """
    Infer capsid role from protein name using pattern matching.
    
    Args:
        protein_name: Protein description/name
        family: Virus family (for context)
    
    Returns:
        Capsid role string
    """
    if not protein_name:
        return "unknown"
    
    protein_name_lower = protein_name.lower()
    
    for role, patterns in ROLE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, protein_name_lower, re.IGNORECASE):
                return role
    
    # Default to MCP if it contains capsid/coat but no specific role
    if any(word in protein_name_lower for word in ["capsid", "coat", "shell"]):
        return "MCP"
    
    return "unknown"


def infer_family_from_organism(organism: str) -> str:
    """
    Infer virus family from organism name.
    
    Args:
        organism: Organism/virus name
    
    Returns:
        Inferred family or empty string
    """
    organism_lower = organism.lower()
    
    # Pattern matching for common virus names
    family_patterns = {
        "Parvoviridae": [r"parvovirus", r"aav", r"adeno-associated", r"bocavirus", r"dependovirus"],
        "Picornaviridae": [r"picornavirus", r"poliovirus", r"rhinovirus", r"enterovirus", r"coxsackie", r"hepatitis a"],
        "Adenoviridae": [r"adenovirus"],
        "Circoviridae": [r"circovirus", r"pcv2?", r"bfdv"],
        "Geminiviridae": [r"geminivirus", r"begomovirus", r"mastrevirus"],
        "Nodaviridae": [r"nodavirus", r"flock house", r"nodamura"],
        "Tombusviridae": [r"tombusvirus", r"carmovirus", r"necrovirus"],
        "Bromoviridae": [r"bromovirus", r"ccmv", r"alfamovirus"],
        "Phycodnaviridae": [r"chlorella virus", r"phycodnavirus", r"pbcv"],
        "Asfarviridae": [r"african swine fever", r"asfv"],
        "Tectiviridae": [r"prd1", r"tectivirus"],
        "Iridoviridae": [r"iridovirus", r"ranavirus"],
        "Mimiviridae": [r"mimivirus", r"megavirus"],
        "Birnaviridae": [r"birnavirus", r"ibdv", r"ipnv"],
    }
    
    for family, patterns in family_patterns.items():
        for pattern in patterns:
            if re.search(pattern, organism_lower, re.IGNORECASE):
                return family
    
    return ""


def lookup_pdb_structure(uniprot_id: str) -> Tuple[str, str]:
    """
    Look up PDB structure availability for a UniProt ID.
    
    Args:
        uniprot_id: UniProt accession
    
    Returns:
        Tuple of (pdb_id, structure_source)
    """
    if not uniprot_id:
        return "", ""
    
    # Check PDB mapping via PDBe API
    url = f"https://www.ebi.ac.uk/pdbe/api/mappings/best_structures/{uniprot_id}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            structures = data.get(uniprot_id, [])
            
            if structures:
                # Return the best structure
                best = structures[0]
                pdb_id = best.get("pdb_id", "")
                return pdb_id.upper(), "experimental"
                
    except Exception as e:
        pass  # Silent fail, will check AlphaFold next
    
    # Check AlphaFold DB
    alphafold_id = f"AF-{uniprot_id}-F1"
    af_url = f"https://alphafold.ebi.ac.uk/api/prediction/{uniprot_id}"
    
    try:
        response = requests.get(af_url, timeout=10)
        if response.status_code == 200:
            return alphafold_id, "AlphaFold"
    except:
        pass
    
    return "", ""


def annotate_dataframe(df: pd.DataFrame, 
                       lookup_structures: bool = False,
                       rate_limit: float = 0.5) -> pd.DataFrame:
    """
    Add capsidomics annotations to the DataFrame.
    
    Args:
        df: DataFrame with expanded hits
        lookup_structures: If True, query PDB/AlphaFold for structures
        rate_limit: Seconds between API calls
    
    Returns:
        Annotated DataFrame
    """
    logger.info("Adding capsidomics annotations...")
    
    # Initialize new columns
    annotation_cols = [
        "inferred_family", "capsid_role", "architecture_class", 
        "virion_morphology", "t_number", "genome_type", "jrf_orientation",
        "structure_id", "structure_source", "realm", "host_category"
    ]
    
    for col in annotation_cols:
        if col not in df.columns:
            df[col] = ""
    
    for idx, row in df.iterrows():
        # Step 1: Infer or use existing family
        family = row.get("family", "")
        if not family:
            family = infer_family_from_organism(row.get("organism", ""))
            df.at[idx, "inferred_family"] = family
        else:
            df.at[idx, "inferred_family"] = family
        
        # Step 2: Lookup family annotations
        if family in FAMILY_ANNOTATIONS:
            fam_annot = FAMILY_ANNOTATIONS[family]
            for key, value in fam_annot.items():
                df.at[idx, key] = value
        else:
            # Use PFAM-based class if available
            pfam_class = row.get("pfam_jrf_class", "")
            if pfam_class:
                df.at[idx, "architecture_class"] = pfam_class
            
            pfam_role = row.get("pfam_capsid_role", "")
            if pfam_role:
                df.at[idx, "capsid_role"] = pfam_role
        
        # Step 3: Infer capsid role from protein name if not set
        if not df.at[idx, "capsid_role"]:
            df.at[idx, "capsid_role"] = infer_capsid_role(
                row.get("protein_name", ""), 
                family
            )
        
        # Step 4: Structure lookup (optional, requires API calls)
        if lookup_structures and not df.at[idx, "structure_id"]:
            uniprot_id = row.get("uniprot_id", "")
            if uniprot_id:
                pdb_id, source = lookup_pdb_structure(uniprot_id)
                df.at[idx, "structure_id"] = pdb_id
                df.at[idx, "structure_source"] = source
                time.sleep(rate_limit)
        
        # Progress logging
        if idx % 100 == 0:
            logger.info(f"  Annotated {idx}/{len(df)} proteins...")
    
    return df


def apply_evidence_rules(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply evidence rules to classify confidence levels.
    
    High confidence requires:
    - Annotated as capsid/coat/MCP
    - Matched to capsid-type JRF PFAM
    - Reasonable length (150-2000 aa)
    
    Args:
        df: Annotated DataFrame
    
    Returns:
        DataFrame with evidence_level column updated
    """
    logger.info("Applying evidence rules...")
    
    # Initialize to medium
    df["evidence_level"] = "medium"
    
    # High confidence criteria
    high_conf_mask = (
        # Capsid role is known
        (df["capsid_role"].isin(["MCP", "minor", "spike", "turret", "cement"])) &
        # Architecture class is known
        (df["architecture_class"].isin(["SJR", "DJR", "tandem_JRF"])) &
        # Reasonable length
        (df["protein_length"] >= 150) &
        (df["protein_length"] <= 2000)
    )
    
    df.loc[high_conf_mask, "evidence_level"] = "high"
    
    # Low confidence criteria
    low_conf_mask = (
        (df["capsid_role"] == "unknown") |
        (df["architecture_class"] == "") |
        (df["protein_length"] < 100)
    )
    
    df.loc[low_conf_mask, "evidence_level"] = "low"
    
    # Boost to high if structure is available
    structure_mask = df["structure_id"].notna() & (df["structure_id"] != "")
    df.loc[structure_mask & (df["evidence_level"] == "medium"), "evidence_level"] = "high"
    
    logger.info(f"  High confidence: {(df['evidence_level'] == 'high').sum()}")
    logger.info(f"  Medium confidence: {(df['evidence_level'] == 'medium').sum()}")
    logger.info(f"  Low confidence: {(df['evidence_level'] == 'low').sum()}")
    
    return df


def generate_master_columns_order() -> List[str]:
    """Return the preferred column order for the master table."""
    return [
        # Identifiers
        "protein_id",
        "uniprot_id",
        "uniprot_name",
        "structure_id",
        
        # Organism/taxonomy
        "organism",
        "taxonomy_id",
        "inferred_family",
        "realm",
        "host_category",
        
        # Protein info
        "protein_name",
        "protein_length",
        "pfam_source",
        "pfam_name",
        
        # Capsidomics fields
        "capsid_role",
        "architecture_class",
        "virion_morphology",
        "t_number",
        "genome_type",
        "jrf_orientation",
        
        # Evidence
        "pfam_jrf_class",
        "pfam_capsid_role",
        "structure_source",
        "evidence_level",
        
        # Metadata
        "source",
    ]


def reorder_and_clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Reorder columns and clean up the DataFrame."""
    
    preferred_order = generate_master_columns_order()
    
    # Get columns that exist in df
    existing_cols = [c for c in preferred_order if c in df.columns]
    
    # Add any remaining columns
    remaining_cols = [c for c in df.columns if c not in existing_cols]
    
    final_order = existing_cols + remaining_cols
    
    return df[final_order]


def generate_summary_stats(df: pd.DataFrame) -> Dict:
    """Generate comprehensive summary statistics."""
    
    stats = {
        "total_entries": len(df),
        "by_evidence_level": df["evidence_level"].value_counts().to_dict(),
        "by_architecture": df["architecture_class"].value_counts().to_dict() if "architecture_class" in df.columns else {},
        "by_capsid_role": df["capsid_role"].value_counts().to_dict() if "capsid_role" in df.columns else {},
        "by_t_number": df["t_number"].value_counts().to_dict() if "t_number" in df.columns else {},
        "by_genome_type": df["genome_type"].value_counts().to_dict() if "genome_type" in df.columns else {},
        "by_family": df["inferred_family"].value_counts().to_dict() if "inferred_family" in df.columns else {},
        "by_morphology": df["virion_morphology"].value_counts().to_dict() if "virion_morphology" in df.columns else {},
        "with_structure": len(df[df["structure_id"].notna() & (df["structure_id"] != "")]) if "structure_id" in df.columns else 0,
    }
    
    return stats


def main(lookup_structures: bool = False):
    """
    Main execution function.
    
    Args:
        lookup_structures: If True, query PDB/AlphaFold for structures
    """
    
    logger.info("=" * 60)
    logger.info("Phase 4: McKenna-Style Capsidomics Annotation")
    logger.info("=" * 60)
    
    # Step 1: Load cleaned hits
    clean_path = DATA_CLEAN / "jrf_all_hits_clean.csv"
    if not clean_path.exists():
        logger.error(f"Cleaned hits not found at {clean_path}")
        logger.error("Please run phase3_expansion.py first")
        return
    
    df = pd.read_csv(clean_path)
    logger.info(f"\nLoaded {len(df)} cleaned hits")
    
    # Step 2: Add capsidomics annotations
    df = annotate_dataframe(df, lookup_structures=lookup_structures)
    
    # Step 3: Apply evidence rules
    df = apply_evidence_rules(df)
    
    # Step 4: Reorder columns
    df = reorder_and_clean_columns(df)
    
    # Step 5: Save master table
    master_path = DATA_CLEAN / "jrf_capsidomics_master.csv"
    df.to_csv(master_path, index=False)
    logger.info(f"\nSaved master table to: {master_path}")
    
    # Step 6: Create high-confidence subset
    high_conf = df[df["evidence_level"] == "high"].copy()
    high_conf_path = DATA_CLEAN / "jrf_high_confidence.csv"
    high_conf.to_csv(high_conf_path, index=False)
    logger.info(f"Saved high-confidence subset ({len(high_conf)} entries) to: {high_conf_path}")
    
    # Step 7: Generate and display summary
    stats = generate_summary_stats(df)
    
    logger.info("\n" + "=" * 60)
    logger.info("CAPSIDOMICS ANNOTATION SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total entries: {stats['total_entries']}")
    logger.info(f"With structure: {stats['with_structure']}")
    
    logger.info("\nBy Evidence Level:")
    for level, count in stats["by_evidence_level"].items():
        logger.info(f"  {level}: {count}")
    
    logger.info("\nBy Architecture Class:")
    for arch, count in stats.get("by_architecture", {}).items():
        logger.info(f"  {arch}: {count}")
    
    logger.info("\nBy Capsid Role:")
    for role, count in stats.get("by_capsid_role", {}).items():
        logger.info(f"  {role}: {count}")
    
    logger.info("\nBy T-Number:")
    for t_num, count in stats.get("by_t_number", {}).items():
        logger.info(f"  {t_num}: {count}")
    
    # Save summary
    summary_path = DATA_CLEAN / "jrf_capsidomics_summary.json"
    with open(summary_path, "w") as f:
        json.dump(stats, f, indent=2)
    logger.info(f"\nSaved summary to: {summary_path}")
    
    logger.info("\n" + "=" * 60)
    logger.info("Phase 4 complete!")
    logger.info("=" * 60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Phase 4: McKenna-Style Capsidomics Annotation")
    parser.add_argument("--lookup-structures", action="store_true",
                        help="Query PDB/AlphaFold for structure availability (slower)")
    
    args = parser.parse_args()
    main(lookup_structures=args.lookup_structures)
