#!/usr/bin/env python3
"""
Phase 3: Expand from PFAM to All Viral Proteins
================================================

This script expands from the curated PFAM domains to identify ALL viral proteins
containing JRF domains across the sequence databases.

Process:
1. For each PFAM in jrf_pfam_master, query InterPro/UniProt for viral members
2. Filter to virus taxonomy only
3. Collect accession IDs, organism info, domain boundaries
4. Clean and deduplicate the dataset
5. Output the "universe" of candidate JRF proteins

Outputs:
- data_raw/jrf_all_hits_raw.csv - Raw expanded hit list
- data_clean/jrf_all_hits_clean.csv - Cleaned and deduplicated

Usage:
    python phase3_expansion.py

Author: JRF Capsidomics Atlas Project
Date: 2026-01-27
"""

import pandas as pd
import requests
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Generator
import logging
from collections import defaultdict
import gzip
import io

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

# Virus taxonomy ID in NCBI
VIRUS_TAXONOMY_ID = 10239


def query_interpro_pfam_members(pfam_id: str, 
                                 taxonomy_filter: str = "Viruses",
                                 max_results: int = 10000) -> List[Dict]:
    """
    Query InterPro API to get all proteins matching a PFAM domain.
    
    Args:
        pfam_id: PFAM accession (e.g., PF00740)
        taxonomy_filter: Taxonomy group to filter (default: Viruses)
        max_results: Maximum number of results to retrieve
    
    Returns:
        List of protein dictionaries
    """
    # InterPro API endpoint for PFAM -> proteins
    base_url = "https://www.ebi.ac.uk/interpro/api/protein/UniProt/entry/pfam"
    url = f"{base_url}/{pfam_id}/?page_size=200"
    
    proteins = []
    page = 1
    
    while url and len(proteins) < max_results:
        try:
            response = requests.get(url, timeout=30)
            if response.status_code != 200:
                logger.warning(f"Failed to fetch {pfam_id} page {page}: HTTP {response.status_code}")
                break
            
            data = response.json()
            
            for result in data.get("results", []):
                metadata = result.get("metadata", {})
                source_organism = metadata.get("source_organism", {})
                
                # Filter for viruses (taxonomy ID 10239)
                tax_id = source_organism.get("taxId", 0)
                lineage = source_organism.get("lineage", "")
                
                # Check if it's a virus
                is_virus = False
                if "Viruses" in lineage or tax_id == VIRUS_TAXONOMY_ID:
                    is_virus = True
                
                # For better virus detection, check taxonomy ID range
                # Many virus taxonomy IDs are in specific ranges
                if not is_virus and tax_id > 0:
                    # This is a heuristic; proper check requires taxonomy lookup
                    pass
                
                protein = {
                    "uniprot_id": metadata.get("accession", ""),
                    "protein_name": metadata.get("name", ""),
                    "organism": source_organism.get("scientificName", ""),
                    "taxonomy_id": tax_id,
                    "taxonomy_lineage": lineage,
                    "is_virus": is_virus,
                    "protein_length": metadata.get("length", 0),
                    "source_database": metadata.get("source_database", {}).get("name", ""),
                    "pfam_source": pfam_id
                }
                
                proteins.append(protein)
            
            # Get next page URL
            url = data.get("next", None)
            page += 1
            
            if page % 5 == 0:
                logger.info(f"  Fetched {len(proteins)} proteins for {pfam_id}...")
            
            time.sleep(0.3)  # Rate limiting
            
        except Exception as e:
            logger.error(f"Error fetching {pfam_id}: {e}")
            break
    
    # Filter to viruses only
    virus_proteins = [p for p in proteins if p["is_virus"]]
    logger.info(f"  {pfam_id}: {len(virus_proteins)}/{len(proteins)} are viral proteins")
    
    return virus_proteins


def query_uniprot_by_pfam(pfam_id: str, max_results: int = 10000) -> List[Dict]:
    """
    Alternative: Query UniProt directly for proteins with a PFAM domain.
    Uses UniProt's new REST API with virus filter.
    
    Args:
        pfam_id: PFAM accession
        max_results: Maximum results
    
    Returns:
        List of protein dictionaries
    """
    base_url = "https://rest.uniprot.org/uniprotkb/search"
    
    # Build query: PFAM domain + virus taxonomy
    query = f'(xref:pfam-{pfam_id}) AND (taxonomy_id:10239)'
    
    params = {
        "query": query,
        "format": "json",
        "size": 500,
        "fields": "accession,id,protein_name,organism_name,organism_id,length,sequence,xref_pfam"
    }
    
    proteins = []
    
    try:
        response = requests.get(base_url, params=params, timeout=30)
        if response.status_code != 200:
            logger.warning(f"UniProt query failed for {pfam_id}: HTTP {response.status_code}")
            return proteins
        
        data = response.json()
        
        for result in data.get("results", []):
            protein = {
                "uniprot_id": result.get("primaryAccession", ""),
                "uniprot_name": result.get("uniProtkbId", ""),
                "protein_name": "",
                "organism": result.get("organism", {}).get("scientificName", ""),
                "taxonomy_id": result.get("organism", {}).get("taxonId", 0),
                "taxonomy_lineage": result.get("organism", {}).get("lineage", []),
                "protein_length": result.get("sequence", {}).get("length", 0),
                "pfam_source": pfam_id,
                "is_virus": True  # Already filtered
            }
            
            # Get protein name from description
            prot_desc = result.get("proteinDescription", {})
            rec_name = prot_desc.get("recommendedName", {})
            if rec_name:
                protein["protein_name"] = rec_name.get("fullName", {}).get("value", "")
            
            proteins.append(protein)
        
        logger.info(f"  {pfam_id}: Found {len(proteins)} viral proteins via UniProt")
        
    except Exception as e:
        logger.error(f"UniProt query error for {pfam_id}: {e}")
    
    return proteins


def batch_expand_pfams(pfam_df: pd.DataFrame, 
                       use_uniprot: bool = True,
                       rate_limit: float = 1.0) -> pd.DataFrame:
    """
    Expand all PFAM domains to their viral protein members.
    
    Args:
        pfam_df: PFAM master DataFrame with pfam_id column
        use_uniprot: If True, use UniProt API; otherwise use InterPro
        rate_limit: Seconds between API calls
    
    Returns:
        DataFrame with all viral protein hits
    """
    all_proteins = []
    
    # Filter to capsid PFAMs for cleaner results
    capsid_pfams = pfam_df[pfam_df["is_capsid_pfam"] == True]["pfam_id"].tolist()
    
    logger.info(f"Expanding {len(capsid_pfams)} capsid PFAM domains...")
    
    for i, pfam_id in enumerate(capsid_pfams):
        logger.info(f"\n[{i+1}/{len(capsid_pfams)}] Processing {pfam_id}...")
        
        if use_uniprot:
            proteins = query_uniprot_by_pfam(pfam_id)
        else:
            proteins = query_interpro_pfam_members(pfam_id)
        
        # Add PFAM classification info
        pfam_info = pfam_df[pfam_df["pfam_id"] == pfam_id].iloc[0].to_dict()
        for prot in proteins:
            prot["pfam_jrf_class"] = pfam_info.get("jrf_class", "")
            prot["pfam_capsid_role"] = pfam_info.get("capsid_role", "")
            prot["pfam_name"] = pfam_info.get("pfam_name", "")
        
        all_proteins.extend(proteins)
        time.sleep(rate_limit)
    
    df = pd.DataFrame(all_proteins)
    logger.info(f"\nTotal viral proteins found: {len(df)}")
    
    return df


def clean_and_deduplicate(df: pd.DataFrame, 
                          min_length: int = 100,
                          max_length: int = 2000) -> pd.DataFrame:
    """
    Clean and deduplicate the raw hit list.
    
    Args:
        df: Raw DataFrame with all hits
        min_length: Minimum protein length (exclude fragments)
        max_length: Maximum protein length (exclude misannotations)
    
    Returns:
        Cleaned and deduplicated DataFrame
    """
    logger.info("\nCleaning and deduplicating...")
    
    initial_count = len(df)
    
    # Step 1: Remove rows with missing essential data
    df = df.dropna(subset=["uniprot_id"])
    logger.info(f"  After removing missing IDs: {len(df)}")
    
    # Step 2: Filter by length
    if "protein_length" in df.columns:
        df = df[(df["protein_length"] >= min_length) & (df["protein_length"] <= max_length)]
        logger.info(f"  After length filter ({min_length}-{max_length} aa): {len(df)}")
    
    # Step 3: Deduplicate by UniProt ID (keep first occurrence with most PFAM info)
    df = df.drop_duplicates(subset=["uniprot_id"], keep="first")
    logger.info(f"  After deduplication: {len(df)}")
    
    # Step 4: Add quality flags
    df["evidence_level"] = "medium"  # Default
    df.loc[df["protein_length"] >= 150, "evidence_level"] = "high"
    df.loc[df["protein_length"] < 150, "evidence_level"] = "low"
    
    logger.info(f"\nRemoved {initial_count - len(df)} entries during cleaning")
    
    return df


def generate_simulated_expansion() -> pd.DataFrame:
    """
    Generate a simulated expansion dataset for demonstration.
    
    This is used when API access is unavailable or for testing.
    In production, use batch_expand_pfams() with real API calls.
    
    Returns:
        DataFrame with simulated expansion results
    """
    logger.info("Generating simulated expansion data (demo mode)...")
    
    # Simulated data representing expected results
    simulated_data = [
        # Parvoviridae examples
        {"uniprot_id": "P03135", "protein_name": "Capsid protein VP1", "organism": "Adeno-associated virus 2", 
         "taxonomy_id": 10804, "protein_length": 735, "pfam_source": "PF00740", "pfam_jrf_class": "SJR", 
         "pfam_capsid_role": "MCP", "family": "Parvoviridae"},
        {"uniprot_id": "A0A0B4J2A1", "protein_name": "Capsid protein", "organism": "Adeno-associated virus 5",
         "taxonomy_id": 68476, "protein_length": 724, "pfam_source": "PF00740", "pfam_jrf_class": "SJR",
         "pfam_capsid_role": "MCP", "family": "Parvoviridae"},
        {"uniprot_id": "P03132", "protein_name": "Capsid protein VP2", "organism": "Canine parvovirus",
         "taxonomy_id": 10786, "protein_length": 584, "pfam_source": "PF00740", "pfam_jrf_class": "SJR",
         "pfam_capsid_role": "MCP", "family": "Parvoviridae"},
         
        # Picornaviridae examples
        {"uniprot_id": "P03300", "protein_name": "Capsid protein VP1", "organism": "Poliovirus type 1",
         "taxonomy_id": 12081, "protein_length": 302, "pfam_source": "PF00729", "pfam_jrf_class": "SJR",
         "pfam_capsid_role": "MCP", "family": "Picornaviridae"},
        {"uniprot_id": "P04936", "protein_name": "Capsid protein VP1", "organism": "Human rhinovirus 14",
         "taxonomy_id": 12130, "protein_length": 289, "pfam_source": "PF00729", "pfam_jrf_class": "SJR",
         "pfam_capsid_role": "MCP", "family": "Picornaviridae"},
         
        # Circoviridae examples
        {"uniprot_id": "Q9YW43", "protein_name": "Capsid protein", "organism": "Porcine circovirus 2",
         "taxonomy_id": 85708, "protein_length": 233, "pfam_source": "PF08398", "pfam_jrf_class": "SJR",
         "pfam_capsid_role": "MCP", "family": "Circoviridae"},
         
        # Adenoviridae examples (DJR)
        {"uniprot_id": "P04133", "protein_name": "Hexon protein", "organism": "Human adenovirus 5",
         "taxonomy_id": 28285, "protein_length": 952, "pfam_source": "PF00608", "pfam_jrf_class": "DJR",
         "pfam_capsid_role": "MCP", "family": "Adenoviridae"},
        {"uniprot_id": "D2Y2S4", "protein_name": "Hexon protein", "organism": "Human adenovirus 26",
         "taxonomy_id": 145628, "protein_length": 946, "pfam_source": "PF00608", "pfam_jrf_class": "DJR",
         "pfam_capsid_role": "MCP", "family": "Adenoviridae"},
         
        # NCLDV examples (DJR)
        {"uniprot_id": "P30316", "protein_name": "Major capsid protein Vp54", "organism": "Paramecium bursaria chlorella virus 1",
         "taxonomy_id": 10506, "protein_length": 437, "pfam_source": "PF04663", "pfam_jrf_class": "DJR",
         "pfam_capsid_role": "MCP", "family": "Phycodnaviridae"},
        {"uniprot_id": "P22035", "protein_name": "Major capsid protein p72", "organism": "African swine fever virus",
         "taxonomy_id": 10497, "protein_length": 646, "pfam_source": "PF04894", "pfam_jrf_class": "DJR",
         "pfam_capsid_role": "MCP", "family": "Asfarviridae"},
         
        # Plant virus examples
        {"uniprot_id": "P03538", "protein_name": "Coat protein", "organism": "Tomato bushy stunt virus",
         "taxonomy_id": 12149, "protein_length": 387, "pfam_source": "PF02227", "pfam_jrf_class": "SJR",
         "pfam_capsid_role": "MCP", "family": "Tombusviridae"},
        {"uniprot_id": "P03600", "protein_name": "Coat protein", "organism": "Cowpea chlorotic mottle virus",
         "taxonomy_id": 12264, "protein_length": 190, "pfam_source": "PF02227", "pfam_jrf_class": "SJR",
         "pfam_capsid_role": "MCP", "family": "Bromoviridae"},
         
        # Bacteriophage examples
        {"uniprot_id": "P27378", "protein_name": "Major capsid protein P3", "organism": "Enterobacteria phage PRD1",
         "taxonomy_id": 10658, "protein_length": 395, "pfam_source": "PF04451", "pfam_jrf_class": "DJR",
         "pfam_capsid_role": "MCP", "family": "Tectiviridae"},
    ]
    
    df = pd.DataFrame(simulated_data)
    
    # Add computed columns
    df["is_virus"] = True
    df["evidence_level"] = "high"
    df["source"] = "simulated_demo"
    
    return df


def main(use_api: bool = False):
    """
    Main execution function.
    
    Args:
        use_api: If True, make real API calls; otherwise use simulated data
    """
    
    logger.info("=" * 60)
    logger.info("Phase 3: PFAM to Viral Protein Expansion")
    logger.info("=" * 60)
    
    # Step 1: Load PFAM master
    pfam_path = DATA_RAW / "jrf_pfam_master.csv"
    if not pfam_path.exists():
        logger.error(f"PFAM master not found at {pfam_path}")
        logger.error("Please run phase2_pfam_mapping.py first")
        return
    
    pfam_df = pd.read_csv(pfam_path)
    logger.info(f"\nLoaded {len(pfam_df)} PFAM domains")
    
    # Step 2: Expand to all viral proteins
    if use_api:
        logger.info("\nUsing API-based expansion (this may take a while)...")
        raw_df = batch_expand_pfams(pfam_df, use_uniprot=True)
    else:
        logger.info("\nUsing simulated data for demonstration...")
        raw_df = generate_simulated_expansion()
    
    # Step 3: Save raw results
    raw_path = DATA_RAW / "jrf_all_hits_raw.csv"
    raw_df.to_csv(raw_path, index=False)
    logger.info(f"\nSaved raw hits to: {raw_path}")
    
    # Step 4: Clean and deduplicate
    clean_df = clean_and_deduplicate(raw_df)
    
    # Step 5: Save clean results
    clean_path = DATA_CLEAN / "jrf_all_hits_clean.csv"
    clean_df.to_csv(clean_path, index=False)
    logger.info(f"Saved cleaned hits to: {clean_path}")
    
    # Step 6: Generate summary
    logger.info("\n" + "=" * 60)
    logger.info("EXPANSION SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Raw hits: {len(raw_df)}")
    logger.info(f"Clean hits: {len(clean_df)}")
    
    if "pfam_jrf_class" in clean_df.columns:
        logger.info("\nBy JRF Class:")
        for cls, count in clean_df["pfam_jrf_class"].value_counts().items():
            logger.info(f"  {cls}: {count}")
    
    if "family" in clean_df.columns:
        logger.info("\nBy Virus Family:")
        for fam, count in clean_df["family"].value_counts().items():
            logger.info(f"  {fam}: {count}")
    
    # Save summary
    summary = {
        "raw_count": len(raw_df),
        "clean_count": len(clean_df),
        "by_jrf_class": clean_df["pfam_jrf_class"].value_counts().to_dict() if "pfam_jrf_class" in clean_df.columns else {},
        "by_family": clean_df["family"].value_counts().to_dict() if "family" in clean_df.columns else {}
    }
    
    summary_path = DATA_CLEAN / "jrf_expansion_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    
    logger.info("\n" + "=" * 60)
    logger.info("Phase 3 complete!")
    logger.info("=" * 60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Phase 3: PFAM to Viral Protein Expansion")
    parser.add_argument("--use-api", action="store_true", 
                        help="Use real API calls instead of simulated data")
    
    args = parser.parse_args()
    main(use_api=args.use_api)
