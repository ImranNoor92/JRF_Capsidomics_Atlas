#!/usr/bin/env python3
"""
JRF Capsidomics Atlas - Complete Pipeline Runner
=================================================

This script runs all phases of the JRF Capsidomics Atlas pipeline.

Usage:
    python run_pipeline.py              # Run all phases (demo mode)
    python run_pipeline.py --full       # Run with API calls (slower, complete)
    python run_pipeline.py --phase 3    # Run only phase 3

Author: JRF Capsidomics Atlas Project
Date: 2026-01-27
"""

import subprocess
import sys
import argparse
from pathlib import Path
import time

# Get script directory
SCRIPT_DIR = Path(__file__).parent / "scripts"

PHASES = [
    ("Phase 1: Build Seed Set", "phase1_seed_set.py", []),
    ("Phase 2: PFAM Mapping", "phase2_pfam_mapping.py", []),
    ("Phase 3: Database Expansion", "phase3_expansion.py", ["--use-api"]),
    ("Phase 4: Capsidomics Annotation", "phase4_annotation.py", ["--lookup-structures"]),
    ("Phase 5: Structural Analysis", "phase5_structural_analysis.py", ["--use-tmalign"]),
    ("Phase 6: Visualization", "phase6_visualization.py", []),
]


def check_dependencies():
    """Check if required packages are installed."""
    required = ['pandas', 'numpy', 'requests']
    optional = ['scipy', 'networkx', 'matplotlib', 'seaborn', 'biopython']
    
    missing_required = []
    missing_optional = []
    
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing_required.append(pkg)
    
    for pkg in optional:
        try:
            __import__(pkg)
        except ImportError:
            missing_optional.append(pkg)
    
    if missing_required:
        print("ERROR: Missing required packages:")
        for pkg in missing_required:
            print(f"  - {pkg}")
        print("\nInstall with: pip install -r requirements.txt")
        return False
    
    if missing_optional:
        print("WARNING: Missing optional packages (some features may be limited):")
        for pkg in missing_optional:
            print(f"  - {pkg}")
        print()
    
    return True


def run_phase(phase_num: int, name: str, script: str, extra_args: list = None, 
              use_full_mode: bool = False):
    """Run a single phase of the pipeline."""
    
    script_path = SCRIPT_DIR / script
    
    if not script_path.exists():
        print(f"ERROR: Script not found: {script_path}")
        return False
    
    print("\n" + "=" * 70)
    print(f"RUNNING: {name}")
    print("=" * 70)
    
    cmd = [sys.executable, str(script_path)]
    
    # Add extra args for full mode
    if use_full_mode and extra_args:
        cmd.extend(extra_args)
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            cmd,
            cwd=str(SCRIPT_DIR),
            check=True
        )
        
        elapsed = time.time() - start_time
        print(f"\n✓ {name} completed in {elapsed:.1f} seconds")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n✗ {name} failed with error code {e.returncode}")
        return False
    except Exception as e:
        print(f"\n✗ {name} failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="JRF Capsidomics Atlas Pipeline Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_pipeline.py              # Run all phases (demo mode)
  python run_pipeline.py --full       # Run with API calls (complete)
  python run_pipeline.py --phase 1    # Run only Phase 1
  python run_pipeline.py --phase 4-6  # Run Phases 4, 5, and 6
        """
    )
    
    parser.add_argument(
        "--full", 
        action="store_true",
        help="Run in full mode with API calls (slower but complete)"
    )
    
    parser.add_argument(
        "--phase",
        type=str,
        help="Run specific phase(s). E.g., '1', '3-5', '1,3,6'"
    )
    
    parser.add_argument(
        "--skip-check",
        action="store_true",
        help="Skip dependency check"
    )
    
    args = parser.parse_args()
    
    # Print header
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                    JRF CAPSIDOMICS ATLAS PIPELINE                    ║
║                                                                      ║
║  A curated map of Jelly-Roll Fold proteins in viral capsids          ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    # Check dependencies
    if not args.skip_check:
        if not check_dependencies():
            sys.exit(1)
    
    # Determine which phases to run
    phases_to_run = list(range(6))  # All phases by default
    
    if args.phase:
        phases_to_run = []
        for part in args.phase.split(","):
            if "-" in part:
                start, end = part.split("-")
                phases_to_run.extend(range(int(start) - 1, int(end)))
            else:
                phases_to_run.append(int(part) - 1)
    
    # Run selected phases
    print(f"Running phases: {[p+1 for p in phases_to_run]}")
    print(f"Mode: {'Full (with API calls)' if args.full else 'Demo (simulated data)'}")
    
    start_time = time.time()
    results = []
    
    for phase_idx in phases_to_run:
        if 0 <= phase_idx < len(PHASES):
            name, script, extra_args = PHASES[phase_idx]
            success = run_phase(
                phase_idx + 1, 
                name, 
                script, 
                extra_args,
                use_full_mode=args.full
            )
            results.append((name, success))
        else:
            print(f"WARNING: Phase {phase_idx + 1} does not exist")
    
    # Print summary
    total_time = time.time() - start_time
    
    print("\n" + "=" * 70)
    print("PIPELINE SUMMARY")
    print("=" * 70)
    
    for name, success in results:
        status = "✓" if success else "✗"
        print(f"  {status} {name}")
    
    successful = sum(1 for _, s in results if s)
    print(f"\nCompleted: {successful}/{len(results)} phases")
    print(f"Total time: {total_time:.1f} seconds")
    
    if all(s for _, s in results):
        print("\n🎉 Pipeline completed successfully!")
        print("\nOutput locations:")
        print("  - Master database: data_clean/jrf_capsidomics_master.csv")
        print("  - High confidence: data_clean/jrf_high_confidence.csv")
        print("  - Analysis files: analyses/")
        print("  - Figures: figures/")
    else:
        print("\n⚠️ Some phases failed. Check the logs above for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
