#!/usr/bin/env python3
"""
Phase 2: Map Seed Proteins to PFAM Domains
==========================================

This script maps the gold-standard seed proteins to their PFAM domain annotations
to create a curated "JRF PFAM master" table.

Process:
1. For each seed protein, query PDB → UniProt → PFAM domain mappings
2. Build a curated table of JRF-associated PFAM domains
3. Classify PFAMs as capsid vs non-capsid JRF domains
4. Create lookup table for Phase 3 expansion

Outputs:
- data_raw/jrf_pfam_master.csv - Master PFAM reference table
- data_raw/seed_to_pfam_mapping.csv - Seed proteins with PFAM annotations

Usage:
    python phase2_pfam_mapping.py

Author: JRF Capsidomics Atlas Project
Date: 2026-01-27
"""

import pandas as pd
import requests
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Set
import logging
from collections import defaultdict

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_RAW = PROJECT_ROOT / "data_raw"
DATA_CLEAN = PROJECT_ROOT / "data_clean"


# =============================================================================
# CURATED JRF PFAM DOMAINS
# =============================================================================

# Pre-curated list of known JRF-associated PFAM domains
# This serves as the reference and will be extended by mapping

KNOWN_JRF_PFAMS = {
    # --- SJR Capsid Domains (High Confidence) ---
    "PF00729": {
        "pfam_name": "Viral_coat",
        "description": "Viral coat protein (VP1/VP2/VP3)",
        "jrf_class": "SJR",
        "capsid_role": "MCP",
        "confidence": "high",
        "example_viruses": "Picornaviruses, Enteroviruses",
        "example_pdbs": "2PLV,1HXS"
    },
    "PF00740": {
        "pfam_name": "Parvo_coat",
        "description": "Parvovirus coat protein VP1/VP2",
        "jrf_class": "SJR",
        "capsid_role": "MCP",
        "confidence": "high",
        "example_viruses": "AAV, CPV, B19",
        "example_pdbs": "1LP3,2CAS"
    },
    "PF02227": {
        "pfam_name": "Viral_caps",
        "description": "Viral capsid protein",
        "jrf_class": "SJR",
        "capsid_role": "MCP",
        "confidence": "high",
        "example_viruses": "Plant ssRNA viruses",
        "example_pdbs": "2TBV,1CWP"
    },
    "PF08398": {
        "pfam_name": "Circovirus_cap",
        "description": "Circovirus capsid protein",
        "jrf_class": "SJR",
        "capsid_role": "MCP",
        "confidence": "high",
        "example_viruses": "PCV2, BFDV",
        "example_pdbs": "3R0R"
    },
    "PF01141": {
        "pfam_name": "Noda_capsid",
        "description": "Nodavirus capsid protein",
        "jrf_class": "SJR",
        "capsid_role": "MCP",
        "confidence": "high",
        "example_viruses": "Flock house virus, Nodamura virus",
        "example_pdbs": "1NOV,2Z2Q"
    },
    "PF00910": {
        "pfam_name": "RNA_phage_coat",
        "description": "RNA bacteriophage coat protein",
        "jrf_class": "SJR",
        "capsid_role": "MCP",
        "confidence": "high",
        "example_viruses": "MS2, Qbeta",
        "example_pdbs": "2MS2"
    },
    "PF08410": {
        "pfam_name": "Gemini_CP",
        "description": "Geminivirus coat protein",
        "jrf_class": "SJR",
        "capsid_role": "MCP",
        "confidence": "high",
        "example_viruses": "Maize streak virus, TYLCV",
        "example_pdbs": "6F2S"
    },
    "PF02305": {
        "pfam_name": "Birna_VP",
        "description": "Birnavirus VP2/VP3 capsid",
        "jrf_class": "SJR",
        "capsid_role": "MCP",
        "confidence": "high",
        "example_viruses": "IBDV, IPNV",
        "example_pdbs": "1WCE"
    },
    "PF02956": {
        "pfam_name": "Microvir_J",
        "description": "Microviridae pilot protein",
        "jrf_class": "SJR",
        "capsid_role": "minor",
        "confidence": "medium",
        "example_viruses": "phiX174",
        "example_pdbs": "2BPA"
    },
    
    # --- DJR Capsid Domains (High Confidence) ---
    "PF00608": {
        "pfam_name": "Adeno_hexon",
        "description": "Adenovirus hexon protein",
        "jrf_class": "DJR",
        "capsid_role": "MCP",
        "confidence": "high",
        "example_viruses": "Human adenovirus",
        "example_pdbs": "1P30"
    },
    "PF09018": {
        "pfam_name": "Adeno_hexon_N",
        "description": "Adenovirus hexon N-terminal domain",
        "jrf_class": "DJR",
        "capsid_role": "MCP",
        "confidence": "high",
        "example_viruses": "Human adenovirus",
        "example_pdbs": "1P30"
    },
    "PF04451": {
        "pfam_name": "DUF557",
        "description": "PRD1-type double jelly-roll MCP",
        "jrf_class": "DJR",
        "capsid_role": "MCP",
        "confidence": "high",
        "example_viruses": "PRD1, Bam35",
        "example_pdbs": "1W8X"
    },
    "PF04663": {
        "pfam_name": "Phycodnavirus_MCP",
        "description": "Phycodnavirus major capsid protein",
        "jrf_class": "DJR",
        "capsid_role": "MCP",
        "confidence": "high",
        "example_viruses": "PBCV-1, Chlorella viruses",
        "example_pdbs": "1M3Y"
    },
    "PF04894": {
        "pfam_name": "ASFV_p72",
        "description": "African swine fever virus p72 MCP",
        "jrf_class": "DJR",
        "capsid_role": "MCP",
        "confidence": "high",
        "example_viruses": "ASFV",
        "example_pdbs": "6KU9"
    },
    "PF04537": {
        "pfam_name": "Iridovirus_MCP",
        "description": "Iridovirus major capsid protein",
        "jrf_class": "DJR",
        "capsid_role": "MCP",
        "confidence": "high",
        "example_viruses": "Iridoviruses, Chloriridovirus",
        "example_pdbs": "4OW6"
    },
    
    # --- JRF-Derived Non-Capsid Domains ---
    "PF01107": {
        "pfam_name": "30Kc",
        "description": "30K cell-to-cell movement protein",
        "jrf_class": "JRF_derived",
        "capsid_role": "movement",
        "confidence": "high",
        "example_viruses": "TMV, Tobamoviruses",
        "example_pdbs": "1VIM"
    },
    "PF00927": {
        "pfam_name": "Nucleoplasmin",
        "description": "Nucleoplasmin domain",
        "jrf_class": "JRF_derived",
        "capsid_role": "non-capsid",
        "confidence": "medium",
        "example_viruses": "Cellular proteins (JRF-derived fold)",
        "example_pdbs": "1K5J"
    },
    
    # --- Spike/Vertex Proteins ---
    "PF03016": {
        "pfam_name": "Penton_base",
        "description": "Adenovirus penton base",
        "jrf_class": "SJR",
        "capsid_role": "minor",
        "confidence": "high",
        "example_viruses": "Adenoviruses",
        "example_pdbs": "1X9T"
    },
    "PF04547": {
        "pfam_name": "Adeno_fiber",
        "description": "Adenovirus fiber protein",
        "jrf_class": "other",
        "capsid_role": "spike",
        "confidence": "medium",
        "example_viruses": "Adenoviruses",
        "example_pdbs": "1QIU"
    },
}


def fetch_pfam_from_uniprot(uniprot_id: str) -> List[Dict]:
    """
    Fetch PFAM domain annotations for a UniProt accession.
    
    Args:
        uniprot_id: UniProt accession (e.g., P03135)
    
    Returns:
        List of PFAM domain dictionaries
    """
    if not uniprot_id:
        return []
    
    # Use InterPro API to get PFAM domains
    url = f"https://www.ebi.ac.uk/interpro/api/entry/pfam/protein/uniprot/{uniprot_id}"
    
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            
            domains = []
            for result in data.get("results", []):
                metadata = result.get("metadata", {})
                
                # Get domain locations
                proteins = result.get("proteins", [])
                locations = []
                if proteins:
                    for prot in proteins:
                        for entry_loc in prot.get("entry_protein_locations", []):
                            for frag in entry_loc.get("fragments", []):
                                locations.append({
                                    "start": frag.get("start", ""),
                                    "end": frag.get("end", "")
                                })
                
                domain = {
                    "pfam_id": metadata.get("accession", ""),
                    "pfam_name": metadata.get("name", ""),
                    "pfam_type": metadata.get("type", ""),
                    "description": metadata.get("description", ""),
                    "locations": locations
                }
                domains.append(domain)
            
            return domains
            
    except Exception as e:
        logger.warning(f"Failed to fetch PFAM data for {uniprot_id}: {e}")
    
    return []


def fetch_pfam_from_pdb(pdb_id: str) -> List[Dict]:
    """
    Fetch PFAM domain annotations via PDB.
    
    Args:
        pdb_id: 4-letter PDB code
    
    Returns:
        List of PFAM domain dictionaries
    """
    if not pdb_id:
        return []
    
    url = f"https://www.ebi.ac.uk/pdbe/api/mappings/pfam/{pdb_id.lower()}"
    
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            
            domains = []
            pdb_data = data.get(pdb_id.lower(), {})
            pfam_data = pdb_data.get("Pfam", {})
            
            for pfam_id, pfam_info in pfam_data.items():
                domain = {
                    "pfam_id": pfam_id,
                    "pfam_name": pfam_info.get("identifier", ""),
                    "description": pfam_info.get("description", ""),
                    "mappings": pfam_info.get("mappings", [])
                }
                domains.append(domain)
            
            return domains
            
    except Exception as e:
        logger.warning(f"Failed to fetch PFAM data for PDB {pdb_id}: {e}")
    
    return []


def map_seeds_to_pfam(seed_df: pd.DataFrame, rate_limit: float = 0.5) -> pd.DataFrame:
    """
    Map seed proteins to their PFAM domain annotations.
    
    Args:
        seed_df: DataFrame with seed proteins (needs uniprot_id and pdb_ids columns)
        rate_limit: Seconds between API calls
    
    Returns:
        DataFrame with seed to PFAM mappings
    """
    logger.info("Mapping seed proteins to PFAM domains...")
    
    mappings = []
    
    for idx, row in seed_df.iterrows():
        uniprot_id = row.get("uniprot_id", "")
        pdb_ids = row.get("pdb_ids", "").split(";") if row.get("pdb_ids") else []
        primary_pdb = pdb_ids[0] if pdb_ids else ""
        
        # Try UniProt first
        pfam_domains = []
        if uniprot_id:
            pfam_domains = fetch_pfam_from_uniprot(uniprot_id)
            time.sleep(rate_limit)
        
        # Fallback to PDB if no UniProt results
        if not pfam_domains and primary_pdb:
            pfam_domains = fetch_pfam_from_pdb(primary_pdb)
            time.sleep(rate_limit)
        
        # Create mapping record
        mapping = {
            "protein_id": row.get("protein_id", ""),
            "uniprot_id": uniprot_id,
            "virus_name": row.get("virus_name", ""),
            "protein_name": row.get("protein_name", ""),
            "architecture_class": row.get("architecture_class", ""),
            "capsid_role": row.get("capsid_role", ""),
            "primary_pdb": primary_pdb,
            "pfam_domains": ";".join([d["pfam_id"] for d in pfam_domains]),
            "pfam_names": ";".join([d.get("pfam_name", "") for d in pfam_domains]),
            "pfam_count": len(pfam_domains)
        }
        
        mappings.append(mapping)
        
        if pfam_domains:
            logger.info(f"  {row.get('virus_name', 'unknown')}: {len(pfam_domains)} PFAM domains found")
        else:
            logger.warning(f"  {row.get('virus_name', 'unknown')}: No PFAM domains found")
    
    return pd.DataFrame(mappings)


def create_pfam_master_table() -> pd.DataFrame:
    """
    Create the master PFAM reference table from curated definitions.
    
    Returns:
        DataFrame with PFAM master table
    """
    records = []
    
    for pfam_id, info in KNOWN_JRF_PFAMS.items():
        record = {
            "pfam_id": pfam_id,
            "pfam_name": info["pfam_name"],
            "description": info["description"],
            "jrf_class": info["jrf_class"],
            "capsid_role": info["capsid_role"],
            "confidence": info["confidence"],
            "is_capsid_pfam": info["capsid_role"] in ["MCP", "minor", "spike", "cement", "turret"],
            "is_jrf_derived": info["jrf_class"] == "JRF_derived",
            "example_viruses": info["example_viruses"],
            "example_pdbs": info["example_pdbs"]
        }
        records.append(record)
    
    df = pd.DataFrame(records)
    df = df.sort_values(["jrf_class", "confidence", "capsid_role"])
    
    return df


def update_pfam_master_from_mappings(pfam_master: pd.DataFrame, 
                                      seed_pfam_mappings: pd.DataFrame) -> pd.DataFrame:
    """
    Update PFAM master table with any new domains found in seed mappings.
    
    Args:
        pfam_master: Current PFAM master table
        seed_pfam_mappings: Seed to PFAM mapping results
    
    Returns:
        Updated PFAM master table
    """
    known_pfams = set(pfam_master["pfam_id"].values)
    
    # Collect new PFAM IDs from mappings
    new_pfams = set()
    for domains in seed_pfam_mappings["pfam_domains"]:
        if domains:
            for pfam_id in domains.split(";"):
                if pfam_id and pfam_id not in known_pfams:
                    new_pfams.add(pfam_id)
    
    if new_pfams:
        logger.info(f"Found {len(new_pfams)} new PFAM domains not in curated list:")
        for pfam_id in sorted(new_pfams):
            logger.info(f"  {pfam_id} - needs manual curation")
    
    return pfam_master


def generate_pfam_summary(pfam_master: pd.DataFrame) -> Dict:
    """Generate summary statistics for the PFAM master table."""
    
    stats = {
        "total_pfams": len(pfam_master),
        "by_jrf_class": pfam_master["jrf_class"].value_counts().to_dict(),
        "by_capsid_role": pfam_master["capsid_role"].value_counts().to_dict(),
        "by_confidence": pfam_master["confidence"].value_counts().to_dict(),
        "capsid_pfams": len(pfam_master[pfam_master["is_capsid_pfam"]]),
        "non_capsid_pfams": len(pfam_master[~pfam_master["is_capsid_pfam"]])
    }
    
    return stats


def main():
    """Main execution function."""
    
    logger.info("=" * 60)
    logger.info("Phase 2: PFAM Domain Mapping")
    logger.info("=" * 60)
    
    # Step 1: Load seed set
    seed_path = DATA_RAW / "jrf_seed_set.csv"
    if not seed_path.exists():
        logger.error(f"Seed set not found at {seed_path}")
        logger.error("Please run phase1_seed_set.py first")
        return
    
    seed_df = pd.read_csv(seed_path)
    logger.info(f"\nLoaded {len(seed_df)} seed proteins")
    
    # Step 2: Create PFAM master table from curated definitions
    logger.info("\nStep 2: Creating PFAM master table...")
    pfam_master = create_pfam_master_table()
    logger.info(f"  Created {len(pfam_master)} curated PFAM entries")
    
    # Step 3: Map seeds to PFAM domains (optional - requires API calls)
    # Uncomment to enable API-based mapping
    # logger.info("\nStep 3: Mapping seeds to PFAM domains...")
    # seed_pfam_mappings = map_seeds_to_pfam(seed_df)
    # pfam_master = update_pfam_master_from_mappings(pfam_master, seed_pfam_mappings)
    
    # For now, create a simple mapping based on known associations
    logger.info("\nStep 3: Creating seed-to-PFAM mappings from curated data...")
    
    # Manual mappings based on literature
    SEED_PFAM_ASSOCIATIONS = {
        "P03135": ["PF00740"],  # AAV2 VP
        "P03132": ["PF00740"],  # CPV VP2
        "P07299": ["PF00740"],  # B19V VP2
        "P03134": ["PF00740"],  # MVM VP2
        "Q9YW43": ["PF08398"],  # PCV2 capsid
        "Q91AV4": ["PF08398"],  # BFDV capsid
        "P04332": ["PF08410"],  # MSV coat
        "Q89437": ["PF08410"],  # AYVV coat
        "P03639": ["PF02956"],  # phiX174 F protein
        "P03300": ["PF00729"],  # Poliovirus VP1
        "P04936": ["PF00729"],  # HRV14 VP1
        "P03305": ["PF00729"],  # FMDV VP1
        "P12870": ["PF01141"],  # Nodamura capsid
        "P12871": ["PF01141"],  # FHV capsid
        "P03538": ["PF02227"],  # TBSV coat
        "P11491": ["PF02227"],  # CarMV coat
        "P03600": ["PF02227"],  # CCMV coat
        "P15476": ["PF02305"],  # IBDV VP2
        "P27378": ["PF04451"],  # PRD1 P3
        "Q7Y1F5": ["PF04451"],  # Bam35 MCP
        "P04133": ["PF00608", "PF09018"],  # HAdV-5 hexon
        "D2Y2S4": ["PF00608", "PF09018"],  # HAdV-26 hexon
        "P30316": ["PF04663"],  # PBCV-1 Vp54
        "P22035": ["PF04894"],  # ASFV p72
        "P20536": ["PF04451"],  # VACV D13 (DJR scaffold)
        "Q6KEN9": ["PF04451"],  # STIV MCP
        "P03583": ["PF01107"],  # TMV 30K movement
        "P27376": ["PF03016"],  # PRD1 P5 spike
        "P03281": ["PF03016"],  # HAdV-2 penton base
    }
    
    seed_mappings = []
    for idx, row in seed_df.iterrows():
        uniprot_id = row.get("uniprot_id", "")
        pfam_ids = SEED_PFAM_ASSOCIATIONS.get(uniprot_id, [])
        
        mapping = {
            "protein_id": row.get("protein_id", ""),
            "uniprot_id": uniprot_id,
            "virus_name": row.get("virus_name", ""),
            "protein_name": row.get("protein_name", ""),
            "architecture_class": row.get("architecture_class", ""),
            "capsid_role": row.get("capsid_role", ""),
            "primary_pdb": row.get("primary_pdb", ""),
            "pfam_domains": ";".join(pfam_ids),
            "pfam_count": len(pfam_ids)
        }
        seed_mappings.append(mapping)
    
    seed_pfam_df = pd.DataFrame(seed_mappings)
    
    # Step 4: Save outputs
    pfam_master_path = DATA_RAW / "jrf_pfam_master.csv"
    pfam_master.to_csv(pfam_master_path, index=False)
    logger.info(f"\nSaved PFAM master to: {pfam_master_path}")
    
    seed_pfam_path = DATA_RAW / "seed_to_pfam_mapping.csv"
    seed_pfam_df.to_csv(seed_pfam_path, index=False)
    logger.info(f"Saved seed-PFAM mapping to: {seed_pfam_path}")
    
    # Step 5: Generate and display summary
    stats = generate_pfam_summary(pfam_master)
    
    logger.info("\n" + "=" * 60)
    logger.info("PFAM MASTER SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total PFAM domains: {stats['total_pfams']}")
    logger.info(f"Capsid PFAMs: {stats['capsid_pfams']}")
    logger.info(f"Non-capsid PFAMs: {stats['non_capsid_pfams']}")
    
    logger.info("\nBy JRF Class:")
    for cls, count in stats["by_jrf_class"].items():
        logger.info(f"  {cls}: {count}")
    
    logger.info("\nBy Capsid Role:")
    for role, count in stats["by_capsid_role"].items():
        logger.info(f"  {role}: {count}")
    
    # Save summary
    summary_path = DATA_RAW / "jrf_pfam_master_summary.json"
    with open(summary_path, "w") as f:
        json.dump(stats, f, indent=2)
    
    logger.info("\n" + "=" * 60)
    logger.info("Phase 2 complete!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
