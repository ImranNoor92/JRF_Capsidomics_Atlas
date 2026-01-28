#!/usr/bin/env python3
"""
Phase 1: Build Gold-Standard Seed Set of Confirmed JRF Proteins
================================================================

This script creates a literature-grounded seed list of confirmed JRF capsid proteins.

The seed set includes:
1. ssDNA capsids (Parvoviridae, Circoviridae, Microviridae, Geminiviridae)
2. Canonical SJR RNA capsid families (Picornaviridae, Nodaviridae, Tombusviridae)
3. DJR lineage representatives (PRD1-adenovirus-giant virus)
4. JRF-derived non-capsid proteins (movement proteins, spike/turret proteins)

Output: data_raw/jrf_seed_set.csv

Usage:
    python phase1_seed_set.py

Author: JRF Capsidomics Atlas Project
Date: 2026-01-27
"""

import pandas as pd
import requests
import json
import time
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_RAW = PROJECT_ROOT / "data_raw"
DATA_CLEAN = PROJECT_ROOT / "data_clean"

# Ensure directories exist
DATA_RAW.mkdir(exist_ok=True)
DATA_CLEAN.mkdir(exist_ok=True)


# =============================================================================
# SEED SET DEFINITIONS
# =============================================================================

# Literature-grounded seed proteins with confirmed JRF capsid structures
# Based on McKenna/Mietzsch parvoviridae work + canonical virus structures

SEED_PROTEINS = [
    # =========================================================================
    # 1. ssDNA CAPSIDS - Single Jelly-Roll (SJR)
    # =========================================================================
    
    # --- Parvoviridae (McKenna/Mietzsch focus) ---
    {
        "virus_name": "Adeno-associated virus 2",
        "virus_abbrev": "AAV2",
        "protein_name": "VP1/VP2/VP3",
        "capsid_role": "MCP",
        "genome_type": "ssDNA",
        "host_category": "Eukaryota_Animal",
        "family": "Parvoviridae",
        "architecture_class": "SJR",
        "t_number": "pseudo-T=3",
        "virion_morphology": "icosahedral",
        "pdb_ids": ["1LP3", "6IH9", "3J1Q"],
        "uniprot_id": "P03135",
        "reference_pmid": "12644448",
        "notes": "Well-characterized gene therapy vector capsid"
    },
    {
        "virus_name": "Canine parvovirus",
        "virus_abbrev": "CPV",
        "protein_name": "VP2",
        "capsid_role": "MCP",
        "genome_type": "ssDNA",
        "host_category": "Eukaryota_Animal",
        "family": "Parvoviridae",
        "architecture_class": "SJR",
        "t_number": "pseudo-T=3",
        "virion_morphology": "icosahedral",
        "pdb_ids": ["2CAS", "4DPV"],
        "uniprot_id": "P03132",
        "reference_pmid": "8709232",
        "notes": "Prototype parvovirus structure"
    },
    {
        "virus_name": "B19 virus",
        "virus_abbrev": "B19V",
        "protein_name": "VP2",
        "capsid_role": "MCP",
        "genome_type": "ssDNA",
        "host_category": "Eukaryota_Animal",
        "family": "Parvoviridae",
        "architecture_class": "SJR",
        "t_number": "pseudo-T=3",
        "virion_morphology": "icosahedral",
        "pdb_ids": ["1S58"],
        "uniprot_id": "P07299",
        "reference_pmid": "15163499",
        "notes": "Human parvovirus"
    },
    {
        "virus_name": "Minute virus of mice",
        "virus_abbrev": "MVM",
        "protein_name": "VP2",
        "capsid_role": "MCP",
        "genome_type": "ssDNA",
        "host_category": "Eukaryota_Animal",
        "family": "Parvoviridae",
        "architecture_class": "SJR",
        "t_number": "pseudo-T=3",
        "virion_morphology": "icosahedral",
        "pdb_ids": ["1MVM"],
        "uniprot_id": "P03134",
        "reference_pmid": "8709232",
        "notes": "Protoparvovirus model"
    },
    
    # --- Circoviridae ---
    {
        "virus_name": "Porcine circovirus 2",
        "virus_abbrev": "PCV2",
        "protein_name": "Capsid protein",
        "capsid_role": "MCP",
        "genome_type": "ssDNA",
        "host_category": "Eukaryota_Animal",
        "family": "Circoviridae",
        "architecture_class": "SJR",
        "t_number": "T=1",
        "virion_morphology": "icosahedral",
        "pdb_ids": ["3R0R"],
        "uniprot_id": "Q9YW43",
        "reference_pmid": "21832183",
        "notes": "Small circular DNA virus"
    },
    {
        "virus_name": "Beak and feather disease virus",
        "virus_abbrev": "BFDV",
        "protein_name": "Capsid protein",
        "capsid_role": "MCP",
        "genome_type": "ssDNA",
        "host_category": "Eukaryota_Animal",
        "family": "Circoviridae",
        "architecture_class": "SJR",
        "t_number": "T=1",
        "virion_morphology": "icosahedral",
        "pdb_ids": ["5ZHG"],
        "uniprot_id": "Q91AV4",
        "reference_pmid": "30111497",
        "notes": "Avian circovirus"
    },
    
    # --- Geminiviridae ---
    {
        "virus_name": "Maize streak virus",
        "virus_abbrev": "MSV",
        "protein_name": "Coat protein",
        "capsid_role": "MCP",
        "genome_type": "ssDNA",
        "host_category": "Eukaryota_Plant",
        "family": "Geminiviridae",
        "architecture_class": "SJR",
        "t_number": "T=1",
        "virion_morphology": "geminate",
        "pdb_ids": ["6F2S"],
        "uniprot_id": "P04332",
        "reference_pmid": "29695621",
        "notes": "Geminate (twinned) capsid structure"
    },
    {
        "virus_name": "Ageratum yellow vein virus",
        "virus_abbrev": "AYVV",
        "protein_name": "Coat protein",
        "capsid_role": "MCP",
        "genome_type": "ssDNA",
        "host_category": "Eukaryota_Plant",
        "family": "Geminiviridae",
        "architecture_class": "SJR",
        "t_number": "T=1",
        "virion_morphology": "geminate",
        "pdb_ids": ["6F2T"],
        "uniprot_id": "Q89437",
        "reference_pmid": "29695621",
        "notes": "Begomovirus"
    },
    
    # --- Microviridae (ssDNA bacteriophages) ---
    {
        "virus_name": "Bacteriophage phiX174",
        "virus_abbrev": "phiX174",
        "protein_name": "F protein (coat)",
        "capsid_role": "MCP",
        "genome_type": "ssDNA",
        "host_category": "Bacteria",
        "family": "Microviridae",
        "architecture_class": "SJR",
        "t_number": "T=1",
        "virion_morphology": "icosahedral",
        "pdb_ids": ["2BPA", "1CD3"],
        "uniprot_id": "P03639",
        "reference_pmid": "8602507",
        "notes": "Classic ssDNA phage"
    },
    
    # =========================================================================
    # 2. ssRNA CAPSIDS - Single Jelly-Roll (SJR)
    # =========================================================================
    
    # --- Picornaviridae ---
    {
        "virus_name": "Poliovirus 1",
        "virus_abbrev": "PV1",
        "protein_name": "VP1",
        "capsid_role": "MCP",
        "genome_type": "ssRNA+",
        "host_category": "Eukaryota_Animal",
        "family": "Picornaviridae",
        "architecture_class": "SJR",
        "t_number": "pseudo-T=3",
        "virion_morphology": "icosahedral",
        "pdb_ids": ["1HXS", "2PLV"],
        "uniprot_id": "P03300",
        "reference_pmid": "2538243",
        "notes": "Prototype picornavirus, 3 SJR proteins per protomer"
    },
    {
        "virus_name": "Human rhinovirus 14",
        "virus_abbrev": "HRV14",
        "protein_name": "VP1",
        "capsid_role": "MCP",
        "genome_type": "ssRNA+",
        "host_category": "Eukaryota_Animal",
        "family": "Picornaviridae",
        "architecture_class": "SJR",
        "t_number": "pseudo-T=3",
        "virion_morphology": "icosahedral",
        "pdb_ids": ["4RHV"],
        "uniprot_id": "P04936",
        "reference_pmid": "3856866",
        "notes": "Common cold virus"
    },
    {
        "virus_name": "Foot-and-mouth disease virus",
        "virus_abbrev": "FMDV",
        "protein_name": "VP1",
        "capsid_role": "MCP",
        "genome_type": "ssRNA+",
        "host_category": "Eukaryota_Animal",
        "family": "Picornaviridae",
        "architecture_class": "SJR",
        "t_number": "pseudo-T=3",
        "virion_morphology": "icosahedral",
        "pdb_ids": ["1BBT"],
        "uniprot_id": "P03305",
        "reference_pmid": "2997611",
        "notes": "Agriculturally important"
    },
    
    # --- Nodaviridae ---
    {
        "virus_name": "Nodamura virus",
        "virus_abbrev": "NoV",
        "protein_name": "Capsid protein alpha",
        "capsid_role": "MCP",
        "genome_type": "ssRNA+",
        "host_category": "Eukaryota_Animal",
        "family": "Nodaviridae",
        "architecture_class": "SJR",
        "t_number": "T=3",
        "virion_morphology": "icosahedral",
        "pdb_ids": ["1NOV"],
        "uniprot_id": "P12870",
        "reference_pmid": "8009220",
        "notes": "T=3 insect virus"
    },
    {
        "virus_name": "Flock house virus",
        "virus_abbrev": "FHV",
        "protein_name": "Capsid protein alpha",
        "capsid_role": "MCP",
        "genome_type": "ssRNA+",
        "host_category": "Eukaryota_Animal",
        "family": "Nodaviridae",
        "architecture_class": "SJR",
        "t_number": "T=3",
        "virion_morphology": "icosahedral",
        "pdb_ids": ["2Z2Q"],
        "uniprot_id": "P12871",
        "reference_pmid": "17981124",
        "notes": "Model for capsid assembly"
    },
    
    # --- Tombusviridae ---
    {
        "virus_name": "Tomato bushy stunt virus",
        "virus_abbrev": "TBSV",
        "protein_name": "Coat protein",
        "capsid_role": "MCP",
        "genome_type": "ssRNA+",
        "host_category": "Eukaryota_Plant",
        "family": "Tombusviridae",
        "architecture_class": "SJR",
        "t_number": "T=3",
        "virion_morphology": "icosahedral",
        "pdb_ids": ["2TBV"],
        "uniprot_id": "P03538",
        "reference_pmid": "17981127",
        "notes": "First T=3 virus structure"
    },
    {
        "virus_name": "Carnation mottle virus",
        "virus_abbrev": "CarMV",
        "protein_name": "Coat protein",
        "capsid_role": "MCP",
        "genome_type": "ssRNA+",
        "host_category": "Eukaryota_Plant",
        "family": "Tombusviridae",
        "architecture_class": "SJR",
        "t_number": "T=3",
        "virion_morphology": "icosahedral",
        "pdb_ids": ["1OPO"],
        "uniprot_id": "P11491",
        "reference_pmid": "14691228",
        "notes": "Plant carmovirus"
    },
    
    # --- Bromoviridae ---
    {
        "virus_name": "Cowpea chlorotic mottle virus",
        "virus_abbrev": "CCMV",
        "protein_name": "Coat protein",
        "capsid_role": "MCP",
        "genome_type": "ssRNA+",
        "host_category": "Eukaryota_Plant",
        "family": "Bromoviridae",
        "architecture_class": "SJR",
        "t_number": "T=3",
        "virion_morphology": "icosahedral",
        "pdb_ids": ["1CWP"],
        "uniprot_id": "P03600",
        "reference_pmid": "7541247",
        "notes": "pH-dependent swelling"
    },
    
    # =========================================================================
    # 3. dsRNA CAPSIDS - Single Jelly-Roll (SJR)
    # =========================================================================
    
    # --- Birnaviridae ---
    {
        "virus_name": "Infectious bursal disease virus",
        "virus_abbrev": "IBDV",
        "protein_name": "VP2",
        "capsid_role": "MCP",
        "genome_type": "dsRNA",
        "host_category": "Eukaryota_Animal",
        "family": "Birnaviridae",
        "architecture_class": "SJR",
        "t_number": "T=13",
        "virion_morphology": "icosahedral",
        "pdb_ids": ["1WCE", "2GSY"],
        "uniprot_id": "P15476",
        "reference_pmid": "15299144",
        "notes": "dsRNA virus with T=13 SJR capsid"
    },
    
    # =========================================================================
    # 4. dsDNA CAPSIDS - Double Jelly-Roll (DJR)
    # =========================================================================
    
    # --- PRD1-like phages ---
    {
        "virus_name": "Bacteriophage PRD1",
        "virus_abbrev": "PRD1",
        "protein_name": "P3 (MCP)",
        "capsid_role": "MCP",
        "genome_type": "dsDNA",
        "host_category": "Bacteria",
        "family": "Tectiviridae",
        "architecture_class": "DJR",
        "t_number": "pseudo-T=25",
        "virion_morphology": "icosahedral",
        "pdb_ids": ["1W8X", "1CJD"],
        "uniprot_id": "P27378",
        "reference_pmid": "15226433",
        "notes": "Prototype DJR MCP"
    },
    {
        "virus_name": "Bacteriophage Bam35",
        "virus_abbrev": "Bam35",
        "protein_name": "MCP",
        "capsid_role": "MCP",
        "genome_type": "dsDNA",
        "host_category": "Bacteria",
        "family": "Tectiviridae",
        "architecture_class": "DJR",
        "t_number": "pseudo-T=25",
        "virion_morphology": "icosahedral",
        "pdb_ids": ["6QVV"],
        "uniprot_id": "Q7Y1F5",
        "reference_pmid": "32265281",
        "notes": "PRD1-like Gram+ phage"
    },
    
    # --- Adenoviridae ---
    {
        "virus_name": "Human adenovirus 5",
        "virus_abbrev": "HAdV-5",
        "protein_name": "Hexon",
        "capsid_role": "MCP",
        "genome_type": "dsDNA",
        "host_category": "Eukaryota_Animal",
        "family": "Adenoviridae",
        "architecture_class": "DJR",
        "t_number": "pseudo-T=25",
        "virion_morphology": "icosahedral",
        "pdb_ids": ["1P30", "6CGV"],
        "uniprot_id": "P04133",
        "reference_pmid": "12552133",
        "notes": "Classic DJR MCP, gene therapy vector"
    },
    {
        "virus_name": "Human adenovirus 26",
        "virus_abbrev": "HAdV-26",
        "protein_name": "Hexon",
        "capsid_role": "MCP",
        "genome_type": "dsDNA",
        "host_category": "Eukaryota_Animal",
        "family": "Adenoviridae",
        "architecture_class": "DJR",
        "t_number": "pseudo-T=25",
        "virion_morphology": "icosahedral",
        "pdb_ids": ["6B1T"],
        "uniprot_id": "D2Y2S4",
        "reference_pmid": "28855253",
        "notes": "Vaccine vector"
    },
    
    # --- Nucleocytoviricota (NCLDVs) ---
    {
        "virus_name": "Paramecium bursaria chlorella virus 1",
        "virus_abbrev": "PBCV-1",
        "protein_name": "Vp54 (MCP)",
        "capsid_role": "MCP",
        "genome_type": "dsDNA",
        "host_category": "Eukaryota_Protist",
        "family": "Phycodnaviridae",
        "architecture_class": "DJR",
        "t_number": "T=169",
        "virion_morphology": "icosahedral",
        "pdb_ids": ["1M3Y"],
        "uniprot_id": "P30316",
        "reference_pmid": "12438624",
        "notes": "Giant virus with DJR MCP"
    },
    {
        "virus_name": "African swine fever virus",
        "virus_abbrev": "ASFV",
        "protein_name": "p72 (MCP)",
        "capsid_role": "MCP",
        "genome_type": "dsDNA",
        "host_category": "Eukaryota_Animal",
        "family": "Asfarviridae",
        "architecture_class": "DJR",
        "t_number": "T=214",
        "virion_morphology": "icosahedral",
        "pdb_ids": ["6KU9"],
        "uniprot_id": "P22035",
        "reference_pmid": "31554923",
        "notes": "Large NCLDV with DJR capsid"
    },
    {
        "virus_name": "Vaccinia virus",
        "virus_abbrev": "VACV",
        "protein_name": "D13 (scaffold)",
        "capsid_role": "minor",
        "genome_type": "dsDNA",
        "host_category": "Eukaryota_Animal",
        "family": "Poxviridae",
        "architecture_class": "DJR",
        "t_number": "NA",
        "virion_morphology": "complex",
        "pdb_ids": ["2YGC"],
        "uniprot_id": "P20536",
        "reference_pmid": "20844023",
        "notes": "DJR scaffold in non-icosahedral virus"
    },
    
    # --- Archaeal viruses with DJR ---
    {
        "virus_name": "Sulfolobus turreted icosahedral virus",
        "virus_abbrev": "STIV",
        "protein_name": "B345 (MCP)",
        "capsid_role": "MCP",
        "genome_type": "dsDNA",
        "host_category": "Archaea",
        "family": "Turriviridae",
        "architecture_class": "DJR",
        "t_number": "pseudo-T=31",
        "virion_morphology": "icosahedral",
        "pdb_ids": ["2BBD"],
        "uniprot_id": "Q6KEN9",
        "reference_pmid": "15886398",
        "notes": "Archaeal virus with turrets"
    },
    
    # =========================================================================
    # 5. JRF-DERIVED NON-CAPSID PROTEINS
    # =========================================================================
    
    # --- Movement proteins (30K superfamily) ---
    {
        "virus_name": "Tobacco mosaic virus",
        "virus_abbrev": "TMV",
        "protein_name": "30K movement protein",
        "capsid_role": "movement",
        "genome_type": "ssRNA+",
        "host_category": "Eukaryota_Plant",
        "family": "Virgaviridae",
        "architecture_class": "JRF_hybrid",
        "t_number": "NA",
        "virion_morphology": "filamentous",
        "pdb_ids": ["1VIM"],
        "uniprot_id": "P03583",
        "reference_pmid": "15016364",
        "notes": "Non-capsid JRF protein, cell-to-cell movement"
    },
    
    # --- Spike/turret proteins ---
    {
        "virus_name": "Bacteriophage PRD1",
        "virus_abbrev": "PRD1",
        "protein_name": "P5 (spike)",
        "capsid_role": "spike",
        "genome_type": "dsDNA",
        "host_category": "Bacteria",
        "family": "Tectiviridae",
        "architecture_class": "SJR",
        "t_number": "NA",
        "virion_morphology": "icosahedral",
        "pdb_ids": ["1YQ8"],
        "uniprot_id": "P27376",
        "reference_pmid": "15919196",
        "notes": "Vertex spike protein, SJR fold"
    },
    {
        "virus_name": "Human adenovirus 2",
        "virus_abbrev": "HAdV-2",
        "protein_name": "Penton base",
        "capsid_role": "minor",
        "genome_type": "dsDNA",
        "host_category": "Eukaryota_Animal",
        "family": "Adenoviridae",
        "architecture_class": "SJR",
        "t_number": "NA",
        "virion_morphology": "icosahedral",
        "pdb_ids": ["1X9T"],
        "uniprot_id": "P03281",
        "reference_pmid": "16321979",
        "notes": "SJR penton base at vertices"
    },
    
    # --- Cement/minor capsid proteins ---
    {
        "virus_name": "Human adenovirus 5",
        "virus_abbrev": "HAdV-5",
        "protein_name": "Protein IX",
        "capsid_role": "cement",
        "genome_type": "dsDNA",
        "host_category": "Eukaryota_Animal",
        "family": "Adenoviridae",
        "architecture_class": "other",
        "t_number": "NA",
        "virion_morphology": "icosahedral",
        "pdb_ids": ["6CGV"],
        "uniprot_id": "P03283",
        "reference_pmid": "29898905",
        "notes": "Cement protein stabilizing capsid"
    },
]


def create_seed_dataframe() -> pd.DataFrame:
    """Convert seed list to pandas DataFrame with proper formatting."""
    
    records = []
    for seed in SEED_PROTEINS:
        record = {
            "protein_id": seed.get("uniprot_id", ""),
            "virus_name": seed["virus_name"],
            "virus_abbrev": seed["virus_abbrev"],
            "protein_name": seed["protein_name"],
            "capsid_role": seed["capsid_role"],
            "genome_type": seed["genome_type"],
            "host_category": seed["host_category"],
            "family": seed["family"],
            "architecture_class": seed["architecture_class"],
            "t_number": seed["t_number"],
            "virion_morphology": seed["virion_morphology"],
            "pdb_ids": ";".join(seed.get("pdb_ids", [])),
            "primary_pdb": seed.get("pdb_ids", [""])[0],
            "uniprot_id": seed.get("uniprot_id", ""),
            "reference_pmid": seed.get("reference_pmid", ""),
            "notes": seed.get("notes", ""),
            "evidence_level": "high",
            "source": "seed_set_v1"
        }
        records.append(record)
    
    df = pd.DataFrame(records)
    return df


def fetch_uniprot_info(uniprot_id: str) -> Optional[Dict]:
    """
    Fetch additional information from UniProt for a given accession.
    
    Args:
        uniprot_id: UniProt accession (e.g., P03135)
    
    Returns:
        Dictionary with UniProt metadata or None if fetch fails
    """
    if not uniprot_id:
        return None
        
    url = f"https://rest.uniprot.org/uniprotkb/{uniprot_id}?format=json"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            # Extract relevant fields
            result = {
                "uniprot_name": data.get("uniProtkbId", ""),
                "protein_length": data.get("sequence", {}).get("length", ""),
                "organism": data.get("organism", {}).get("scientificName", ""),
                "taxonomy_id": data.get("organism", {}).get("taxonId", ""),
                "gene_name": "",
                "protein_description": "",
                "reviewed": "reviewed" if data.get("entryType") == "UniProtKB reviewed (Swiss-Prot)" else "unreviewed"
            }
            
            # Get gene name
            genes = data.get("genes", [])
            if genes:
                result["gene_name"] = genes[0].get("geneName", {}).get("value", "")
            
            # Get protein description
            descriptions = data.get("proteinDescription", {})
            rec_name = descriptions.get("recommendedName", {})
            if rec_name:
                result["protein_description"] = rec_name.get("fullName", {}).get("value", "")
            
            return result
            
    except Exception as e:
        logger.warning(f"Failed to fetch UniProt data for {uniprot_id}: {e}")
    
    return None


def enrich_with_uniprot(df: pd.DataFrame, rate_limit: float = 0.5) -> pd.DataFrame:
    """
    Enrich seed DataFrame with UniProt metadata.
    
    Args:
        df: Seed DataFrame with uniprot_id column
        rate_limit: Seconds between API calls
    
    Returns:
        Enriched DataFrame
    """
    logger.info("Enriching with UniProt data...")
    
    # Add new columns
    new_cols = ["uniprot_name", "protein_length", "organism", "taxonomy_id", 
                "gene_name", "protein_description", "reviewed"]
    for col in new_cols:
        df[col] = ""
    
    for idx, row in df.iterrows():
        uniprot_id = row["uniprot_id"]
        if uniprot_id:
            info = fetch_uniprot_info(uniprot_id)
            if info:
                for col in new_cols:
                    df.at[idx, col] = info.get(col, "")
                logger.info(f"  Fetched: {uniprot_id} -> {info.get('organism', 'unknown')}")
            time.sleep(rate_limit)  # Rate limiting
    
    return df


def generate_summary_stats(df: pd.DataFrame) -> Dict:
    """Generate summary statistics for the seed set."""
    
    stats = {
        "total_proteins": len(df),
        "by_architecture": df["architecture_class"].value_counts().to_dict(),
        "by_genome_type": df["genome_type"].value_counts().to_dict(),
        "by_host": df["host_category"].value_counts().to_dict(),
        "by_capsid_role": df["capsid_role"].value_counts().to_dict(),
        "by_family": df["family"].value_counts().to_dict(),
        "with_pdb": len(df[df["primary_pdb"] != ""]),
        "with_uniprot": len(df[df["uniprot_id"] != ""])
    }
    
    return stats


def main():
    """Main execution function."""
    
    logger.info("=" * 60)
    logger.info("Phase 1: Building Gold-Standard JRF Seed Set")
    logger.info("=" * 60)
    
    # Step 1: Create base DataFrame
    logger.info("\nStep 1: Creating seed DataFrame...")
    df = create_seed_dataframe()
    logger.info(f"  Created {len(df)} seed entries")
    
    # Step 2: Optionally enrich with UniProt data
    # Comment out to skip API calls during testing
    # df = enrich_with_uniprot(df)
    
    # Step 3: Save raw seed set
    output_path = DATA_RAW / "jrf_seed_set.csv"
    df.to_csv(output_path, index=False)
    logger.info(f"\nSaved seed set to: {output_path}")
    
    # Step 4: Generate and display summary
    stats = generate_summary_stats(df)
    
    logger.info("\n" + "=" * 60)
    logger.info("SEED SET SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total proteins: {stats['total_proteins']}")
    logger.info(f"With PDB structure: {stats['with_pdb']}")
    logger.info(f"With UniProt ID: {stats['with_uniprot']}")
    
    logger.info("\nBy Architecture Class:")
    for arch, count in stats["by_architecture"].items():
        logger.info(f"  {arch}: {count}")
    
    logger.info("\nBy Genome Type:")
    for gt, count in stats["by_genome_type"].items():
        logger.info(f"  {gt}: {count}")
    
    logger.info("\nBy Capsid Role:")
    for role, count in stats["by_capsid_role"].items():
        logger.info(f"  {role}: {count}")
    
    # Step 5: Save summary to JSON
    import json
    summary_path = DATA_RAW / "jrf_seed_set_summary.json"
    with open(summary_path, "w") as f:
        json.dump(stats, f, indent=2)
    logger.info(f"\nSaved summary to: {summary_path}")
    
    logger.info("\n" + "=" * 60)
    logger.info("Phase 1 complete!")
    logger.info("=" * 60)
    
    return df


if __name__ == "__main__":
    main()
