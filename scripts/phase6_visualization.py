#!/usr/bin/env python3
"""
Phase 6: McKenna-Style Visualization and Final Synthesis
=========================================================

This script generates publication-quality figures and summary tables
following the McKenna/Mietzsch capsidomics style.

Outputs:
1. Summary tables (CSV/Excel format)
   - JRF families overview
   - Structural coverage by architecture
   - T-number distribution
   - Host/genome type matrix

2. Figures
   - Coverage maps (genome type vs architecture)
   - T-number distribution plots
   - Host distribution pie charts
   - Structural lineage schematic

3. Statistical summaries

Usage:
    python phase6_visualization.py

Author: JRF Capsidomics Atlas Project
Date: 2026-01-27
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from typing import Dict, List, Optional
import logging
from collections import Counter

# Optional imports
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import seaborn as sns
    HAS_PLOTTING = True
except ImportError:
    HAS_PLOTTING = False

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_RAW = PROJECT_ROOT / "data_raw"
DATA_CLEAN = PROJECT_ROOT / "data_clean"
ANALYSES = PROJECT_ROOT / "analyses"
FIGURES = PROJECT_ROOT / "figures"

# Ensure directories exist
ANALYSES.mkdir(exist_ok=True)
FIGURES.mkdir(exist_ok=True)

# Color schemes
ARCHITECTURE_COLORS = {
    "SJR": "#3498db",
    "DJR": "#e74c3c",
    "tandem_JRF": "#9b59b6",
    "JRF_hybrid": "#f39c12",
    "JRF_derived": "#2ecc71",
    "other": "#95a5a6"
}

GENOME_COLORS = {
    "ssDNA": "#e74c3c",
    "dsDNA": "#8e44ad",
    "ssRNA+": "#27ae60",
    "ssRNA-": "#16a085",
    "dsRNA": "#f39c12"
}

HOST_COLORS = {
    "Eukaryota_Animal": "#3498db",
    "Eukaryota_Plant": "#2ecc71",
    "Bacteria": "#e74c3c",
    "Archaea": "#9b59b6",
    "Eukaryota_Fungi": "#f39c12",
    "Eukaryota_Protist": "#1abc9c"
}


def load_master_data() -> Optional[pd.DataFrame]:
    """Load the master capsidomics database."""
    
    # Try master table first
    master_path = DATA_CLEAN / "jrf_capsidomics_master.csv"
    if master_path.exists():
        df = pd.read_csv(master_path)
        logger.info(f"Loaded master table: {len(df)} entries")
        return df
    
    # Fall back to high confidence
    hc_path = DATA_CLEAN / "jrf_high_confidence.csv"
    if hc_path.exists():
        df = pd.read_csv(hc_path)
        logger.info(f"Loaded high-confidence table: {len(df)} entries")
        return df
    
    # Fall back to seed set
    seed_path = DATA_RAW / "jrf_seed_set.csv"
    if seed_path.exists():
        df = pd.read_csv(seed_path)
        logger.info(f"Loaded seed set: {len(df)} entries")
        return df
    
    logger.error("No data files found. Please run previous phases first.")
    return None


def generate_family_overview_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate a summary table of JRF virus families.
    
    Args:
        df: Master database
    
    Returns:
        Summary DataFrame
    """
    logger.info("Generating family overview table...")
    
    # Determine family column
    family_col = "inferred_family" if "inferred_family" in df.columns else "family"
    if family_col not in df.columns:
        logger.warning("No family column found")
        return pd.DataFrame()
    
    # Group by family
    family_stats = []
    
    for family in df[family_col].dropna().unique():
        if not family or family == "":
            continue
            
        fam_df = df[df[family_col] == family]
        
        stats = {
            "Family": family,
            "Protein Count": len(fam_df),
            "Architecture": fam_df["architecture_class"].mode()[0] if "architecture_class" in fam_df.columns and len(fam_df["architecture_class"].dropna()) > 0 else "Unknown",
            "Genome Type": fam_df["genome_type"].mode()[0] if "genome_type" in fam_df.columns and len(fam_df["genome_type"].dropna()) > 0 else "Unknown",
            "T-Number": fam_df["t_number"].mode()[0] if "t_number" in fam_df.columns and len(fam_df["t_number"].dropna()) > 0 else "Unknown",
            "With Structure": len(fam_df[fam_df["structure_id"].notna() & (fam_df["structure_id"] != "")]) if "structure_id" in fam_df.columns else 0,
            "High Confidence": len(fam_df[fam_df["evidence_level"] == "high"]) if "evidence_level" in fam_df.columns else 0
        }
        
        family_stats.append(stats)
    
    summary_df = pd.DataFrame(family_stats)
    summary_df = summary_df.sort_values("Protein Count", ascending=False)
    
    return summary_df


def generate_architecture_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate summary by architecture class.
    
    Args:
        df: Master database
    
    Returns:
        Summary DataFrame
    """
    logger.info("Generating architecture summary...")
    
    if "architecture_class" not in df.columns:
        return pd.DataFrame()
    
    arch_stats = []
    
    for arch in df["architecture_class"].dropna().unique():
        if not arch or arch == "":
            continue
            
        arch_df = df[df["architecture_class"] == arch]
        
        stats = {
            "Architecture": arch,
            "Total Proteins": len(arch_df),
            "Families": len(arch_df["inferred_family"].dropna().unique()) if "inferred_family" in arch_df.columns else 0,
            "Genome Types": ", ".join(arch_df["genome_type"].dropna().unique()[:3]) if "genome_type" in arch_df.columns else "",
            "T-Numbers": ", ".join(arch_df["t_number"].dropna().unique()[:5]) if "t_number" in arch_df.columns else "",
            "With Structure (%)": round(100 * len(arch_df[arch_df.get("structure_id", pd.Series()).notna()]) / len(arch_df), 1) if len(arch_df) > 0 else 0
        }
        
        arch_stats.append(stats)
    
    summary_df = pd.DataFrame(arch_stats)
    summary_df = summary_df.sort_values("Total Proteins", ascending=False)
    
    return summary_df


def generate_genome_architecture_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate a cross-tabulation of genome types vs architectures.
    
    Args:
        df: Master database
    
    Returns:
        Cross-tabulation DataFrame
    """
    logger.info("Generating genome x architecture matrix...")
    
    if "genome_type" not in df.columns or "architecture_class" not in df.columns:
        return pd.DataFrame()
    
    matrix = pd.crosstab(
        df["genome_type"],
        df["architecture_class"],
        margins=True,
        margins_name="Total"
    )
    
    return matrix


def plot_architecture_distribution(df: pd.DataFrame, output_path: Path):
    """
    Create a pie chart of architecture class distribution.
    """
    if not HAS_PLOTTING or "architecture_class" not in df.columns:
        return
    
    logger.info("Creating architecture distribution plot...")
    
    counts = df["architecture_class"].value_counts()
    colors = [ARCHITECTURE_COLORS.get(a, "#95a5a6") for a in counts.index]
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    wedges, texts, autotexts = ax.pie(
        counts.values,
        labels=counts.index,
        colors=colors,
        autopct='%1.1f%%',
        pctdistance=0.75,
        startangle=90
    )
    
    ax.set_title("JRF Architecture Class Distribution", fontsize=14, fontweight='bold')
    
    # Add count legend
    legend_labels = [f"{arch}: {count}" for arch, count in zip(counts.index, counts.values)]
    ax.legend(wedges, legend_labels, title="Count", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    logger.info(f"  Saved: {output_path}")


def plot_genome_type_distribution(df: pd.DataFrame, output_path: Path):
    """
    Create a bar chart of genome type distribution.
    """
    if not HAS_PLOTTING or "genome_type" not in df.columns:
        return
    
    logger.info("Creating genome type distribution plot...")
    
    counts = df["genome_type"].value_counts()
    colors = [GENOME_COLORS.get(g, "#95a5a6") for g in counts.index]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    bars = ax.bar(counts.index, counts.values, color=colors, edgecolor='black', linewidth=0.5)
    
    ax.set_xlabel("Genome Type", fontsize=12)
    ax.set_ylabel("Number of Proteins", fontsize=12)
    ax.set_title("JRF Proteins by Genome Type", fontsize=14, fontweight='bold')
    
    # Add value labels on bars
    for bar, count in zip(bars, counts.values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                str(count), ha='center', va='bottom', fontsize=10)
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    logger.info(f"  Saved: {output_path}")


def plot_t_number_distribution(df: pd.DataFrame, output_path: Path):
    """
    Create a bar chart of T-number distribution.
    """
    if not HAS_PLOTTING or "t_number" not in df.columns:
        return
    
    logger.info("Creating T-number distribution plot...")
    
    # Order T-numbers logically
    t_order = ["T=1", "T=3", "pseudo-T=3", "T=7", "T=13", "pseudo-T=25", "higher", "NA"]
    
    counts = df["t_number"].value_counts()
    # Reorder
    ordered_counts = pd.Series(dtype=int)
    for t in t_order:
        if t in counts.index:
            ordered_counts[t] = counts[t]
    for t in counts.index:
        if t not in ordered_counts.index:
            ordered_counts[t] = counts[t]
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    colors = plt.cm.viridis(np.linspace(0, 0.8, len(ordered_counts)))
    bars = ax.bar(ordered_counts.index, ordered_counts.values, color=colors, edgecolor='black', linewidth=0.5)
    
    ax.set_xlabel("T-Number", fontsize=12)
    ax.set_ylabel("Number of Proteins", fontsize=12)
    ax.set_title("JRF Capsid Proteins by Triangulation Number", fontsize=14, fontweight='bold')
    
    for bar, count in zip(bars, ordered_counts.values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                str(count), ha='center', va='bottom', fontsize=9)
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    logger.info(f"  Saved: {output_path}")


def plot_genome_architecture_heatmap(df: pd.DataFrame, output_path: Path):
    """
    Create a heatmap of genome type vs architecture class.
    """
    if not HAS_PLOTTING:
        return
    
    if "genome_type" not in df.columns or "architecture_class" not in df.columns:
        return
    
    logger.info("Creating genome x architecture heatmap...")
    
    matrix = pd.crosstab(df["genome_type"], df["architecture_class"])
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    sns.heatmap(matrix, 
                annot=True, 
                fmt='d', 
                cmap='YlOrRd',
                linewidths=0.5,
                ax=ax)
    
    ax.set_xlabel("Architecture Class", fontsize=12)
    ax.set_ylabel("Genome Type", fontsize=12)
    ax.set_title("JRF Proteins: Genome Type vs Architecture", fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    logger.info(f"  Saved: {output_path}")


def plot_family_overview(df: pd.DataFrame, output_path: Path, top_n: int = 15):
    """
    Create a horizontal bar chart of top families.
    """
    if not HAS_PLOTTING:
        return
    
    family_col = "inferred_family" if "inferred_family" in df.columns else "family"
    if family_col not in df.columns:
        return
    
    logger.info("Creating family overview plot...")
    
    counts = df[family_col].value_counts().head(top_n)
    
    # Get architecture for color coding
    family_arch = {}
    for fam in counts.index:
        fam_df = df[df[family_col] == fam]
        if "architecture_class" in fam_df.columns and len(fam_df) > 0:
            mode = fam_df["architecture_class"].mode()
            if len(mode) > 0:
                family_arch[fam] = mode[0]
            else:
                family_arch[fam] = "other"
        else:
            family_arch[fam] = "other"
    
    colors = [ARCHITECTURE_COLORS.get(family_arch.get(f, "other"), "#95a5a6") for f in counts.index]
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    y_pos = range(len(counts))
    bars = ax.barh(y_pos, counts.values, color=colors, edgecolor='black', linewidth=0.5)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(counts.index)
    ax.invert_yaxis()
    
    ax.set_xlabel("Number of Proteins", fontsize=12)
    ax.set_ylabel("Virus Family", fontsize=12)
    ax.set_title(f"Top {top_n} JRF-Containing Virus Families", fontsize=14, fontweight='bold')
    
    # Add value labels
    for bar, count in zip(bars, counts.values):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                str(count), ha='left', va='center', fontsize=9)
    
    # Add legend for architectures
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=color, label=arch) for arch, color in ARCHITECTURE_COLORS.items()]
    ax.legend(handles=legend_elements, title="Architecture", loc='lower right')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    logger.info(f"  Saved: {output_path}")


def create_evolutionary_schematic_text() -> str:
    """
    Generate a text-based evolutionary schematic.
    
    Returns:
        ASCII art schematic
    """
    schematic = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    JRF EVOLUTIONARY LINEAGE SCHEMATIC                         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║                              ┌─────────────┐                                 ║
║                              │  Ancestral  │                                 ║
║                              │    SJR      │                                 ║
║                              └──────┬──────┘                                 ║
║                                     │                                        ║
║              ┌──────────────────────┼──────────────────────┐                ║
║              │                      │                      │                ║
║              ▼                      ▼                      ▼                ║
║     ┌────────────────┐    ┌────────────────┐    ┌────────────────┐         ║
║     │  RNA Virus     │    │  ssDNA Virus   │    │ Gene Duplication│         ║
║     │  SJR Capsids   │    │  SJR Capsids   │    │      Event      │         ║
║     └───────┬────────┘    └───────┬────────┘    └───────┬────────┘         ║
║             │                     │                     │                   ║
║    ┌────────┼────────┐   ┌───────┼───────┐             ▼                   ║
║    ▼        ▼        ▼   ▼       ▼       ▼    ┌────────────────┐           ║
║ ┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐│      DJR       │           ║
║ │Picorna││Noda- ││Tombus││Parvo-││Circo-││Gemini││   (PRD1-like)  │           ║
║ │viridae││viridae││viridae││viridae││viridae││viridae│└───────┬────────┘           ║
║ │(pT=3) ││(T=3) ││(T=3) ││(pT=3)││(T=1) ││(T=1) │        │                   ║
║ └──────┘└──────┘└──────┘└──────┘└──────┘└──────┘        │                   ║
║                                                          │                   ║
║                              ┌──────────────────────────┼───────────────────┐║
║                              │                          │                   │║
║                              ▼                          ▼                   ▼║
║                    ┌────────────────┐         ┌────────────────┐  ┌──────────────┐║
║                    │  Tectiviridae  │         │  Adenoviridae  │  │    NCLDVs    │║
║                    │  (PRD1, pT=25) │         │   (pT=25)      │  │  (T>100)     │║
║                    └────────────────┘         └────────────────┘  └──────────────┘║
║                                                                              ║
║     ═══════════════════ NEOFUNCTIONALIZATION ═══════════════════            ║
║                                                                              ║
║     SJR Capsid ──────────────────────────▶ Movement Proteins (30K)          ║
║     DJR Capsid ──────────────────────────▶ Scaffold Proteins (Poxvirus D13) ║
║     SJR Capsid ──────────────────────────▶ Nucleoplasmin-like               ║
║                                                                              ║
║     ════════════════════ KEY OBSERVATIONS ══════════════════════            ║
║                                                                              ║
║     • SJR orientation: Tangential (sheets parallel to surface)               ║
║     • DJR orientation: Perpendicular (β-barrels point outward)              ║
║     • T-number correlates with variable region insertions                   ║
║     • DJR likely arose from SJR tandem duplication                          ║
║     • DJR lineage shows vertical inheritance: Bacteria → Archaea → Eukarya  ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
    return schematic


def generate_summary_statistics(df: pd.DataFrame) -> Dict:
    """
    Generate comprehensive summary statistics.
    """
    logger.info("Generating summary statistics...")
    
    stats = {
        "total_entries": len(df),
        "unique_families": len(df["inferred_family"].dropna().unique()) if "inferred_family" in df.columns else 0,
        "architecture_distribution": df["architecture_class"].value_counts().to_dict() if "architecture_class" in df.columns else {},
        "genome_type_distribution": df["genome_type"].value_counts().to_dict() if "genome_type" in df.columns else {},
        "t_number_distribution": df["t_number"].value_counts().to_dict() if "t_number" in df.columns else {},
        "capsid_role_distribution": df["capsid_role"].value_counts().to_dict() if "capsid_role" in df.columns else {},
        "evidence_level_distribution": df["evidence_level"].value_counts().to_dict() if "evidence_level" in df.columns else {},
        "with_structure": len(df[df["structure_id"].notna() & (df["structure_id"] != "")]) if "structure_id" in df.columns else 0,
        "sjr_count": len(df[df["architecture_class"] == "SJR"]) if "architecture_class" in df.columns else 0,
        "djr_count": len(df[df["architecture_class"] == "DJR"]) if "architecture_class" in df.columns else 0,
    }
    
    return stats


def main():
    """Main execution function."""
    
    logger.info("=" * 60)
    logger.info("Phase 6: McKenna-Style Visualization & Synthesis")
    logger.info("=" * 60)
    
    # Step 1: Load data
    df = load_master_data()
    if df is None:
        return
    
    # Step 2: Generate summary tables
    logger.info("\nStep 2: Generating summary tables...")
    
    # Family overview
    family_table = generate_family_overview_table(df)
    if not family_table.empty:
        family_path = ANALYSES / "summary_family_overview.csv"
        family_table.to_csv(family_path, index=False)
        logger.info(f"  Saved: {family_path}")
    
    # Architecture summary
    arch_table = generate_architecture_summary(df)
    if not arch_table.empty:
        arch_path = ANALYSES / "summary_architecture.csv"
        arch_table.to_csv(arch_path, index=False)
        logger.info(f"  Saved: {arch_path}")
    
    # Genome x Architecture matrix
    matrix = generate_genome_architecture_matrix(df)
    if not matrix.empty:
        matrix_path = ANALYSES / "genome_architecture_matrix.csv"
        matrix.to_csv(matrix_path)
        logger.info(f"  Saved: {matrix_path}")
    
    # Step 3: Generate figures
    logger.info("\nStep 3: Generating figures...")
    
    if HAS_PLOTTING:
        # Architecture distribution
        plot_architecture_distribution(df, FIGURES / "architecture_distribution.png")
        
        # Genome type distribution
        plot_genome_type_distribution(df, FIGURES / "genome_type_distribution.png")
        
        # T-number distribution
        plot_t_number_distribution(df, FIGURES / "t_number_distribution.png")
        
        # Genome x Architecture heatmap
        plot_genome_architecture_heatmap(df, FIGURES / "genome_architecture_heatmap.png")
        
        # Family overview
        plot_family_overview(df, FIGURES / "family_overview.png")
    else:
        logger.warning("Matplotlib not available. Skipping figure generation.")
    
    # Step 4: Generate evolutionary schematic
    logger.info("\nStep 4: Generating evolutionary schematic...")
    schematic = create_evolutionary_schematic_text()
    schematic_path = FIGURES / "evolutionary_schematic.txt"
    with open(schematic_path, "w") as f:
        f.write(schematic)
    logger.info(f"  Saved: {schematic_path}")
    
    # Step 5: Generate summary statistics
    logger.info("\nStep 5: Generating summary statistics...")
    stats = generate_summary_statistics(df)
    stats_path = ANALYSES / "final_summary_statistics.json"
    with open(stats_path, "w") as f:
        json.dump(stats, f, indent=2)
    logger.info(f"  Saved: {stats_path}")
    
    # Display summary
    logger.info("\n" + "=" * 60)
    logger.info("FINAL SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total entries in atlas: {stats['total_entries']}")
    logger.info(f"Unique families: {stats['unique_families']}")
    logger.info(f"SJR proteins: {stats['sjr_count']}")
    logger.info(f"DJR proteins: {stats['djr_count']}")
    logger.info(f"With structural data: {stats['with_structure']}")
    
    logger.info("\nOutput files generated:")
    logger.info("  Summary tables:")
    logger.info(f"    - {ANALYSES / 'summary_family_overview.csv'}")
    logger.info(f"    - {ANALYSES / 'summary_architecture.csv'}")
    logger.info(f"    - {ANALYSES / 'genome_architecture_matrix.csv'}")
    logger.info(f"    - {ANALYSES / 'final_summary_statistics.json'}")
    
    if HAS_PLOTTING:
        logger.info("  Figures:")
        logger.info(f"    - {FIGURES / 'architecture_distribution.png'}")
        logger.info(f"    - {FIGURES / 'genome_type_distribution.png'}")
        logger.info(f"    - {FIGURES / 't_number_distribution.png'}")
        logger.info(f"    - {FIGURES / 'genome_architecture_heatmap.png'}")
        logger.info(f"    - {FIGURES / 'family_overview.png'}")
    
    logger.info(f"  Schematic:")
    logger.info(f"    - {FIGURES / 'evolutionary_schematic.txt'}")
    
    logger.info("\n" + "=" * 60)
    logger.info("Phase 6 complete!")
    logger.info("=" * 60)
    logger.info("\n🎉 JRF Capsidomics Atlas pipeline complete!")
    logger.info("Review outputs in data_clean/, analyses/, and figures/ directories.")


if __name__ == "__main__":
    main()
