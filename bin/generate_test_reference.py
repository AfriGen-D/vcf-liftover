#!/usr/bin/env python3
"""
Generate test reference FASTA from full GRCh38 reference genome
Extracts specific chromosomes and regions for testing purposes
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(cmd, description="", use_singularity=True):
    """Run a shell command and handle errors"""
    print(f"Running: {description}")

    # Use singularity for samtools commands
    if use_singularity and 'samtools' in cmd:
        cmd = f"singularity exec /users/mamana/.singularity/quay.io-biocontainers-samtools-1.17--h00cdaf9_0.img {cmd}"

    print(f"Command: {cmd}")

    try:
        result = subprocess.run(cmd, shell=True, check=True,
                              capture_output=True, text=True)
        if result.stdout:
            print(f"Output: {result.stdout.strip()}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print(f"Stderr: {e.stderr}")
        sys.exit(1)

def check_dependencies():
    """Check if required tools are available"""
    print("Checking dependencies...")

    # Check if singularity samtools container is available
    try:
        cmd = "singularity exec /users/mamana/.singularity/quay.io-biocontainers-samtools-1.17--h00cdaf9_0.img samtools --version"
        result = subprocess.run(cmd, shell=True, capture_output=True, check=True)
        print(f"✓ samtools is available via singularity")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: samtools container not available")
        print("Please ensure singularity and samtools container are available")
        sys.exit(1)

def extract_chromosome_regions(input_fasta, output_fasta, regions):
    """Extract specific chromosome regions using samtools"""
    
    print(f"\nExtracting regions from {input_fasta}...")
    
    # Check if input FASTA exists
    if not os.path.exists(input_fasta):
        print(f"Error: Input FASTA not found: {input_fasta}")
        sys.exit(1)
    
    # Check if FASTA index exists, create if not
    fai_file = f"{input_fasta}.fai"
    if not os.path.exists(fai_file):
        print(f"Creating FASTA index...")
        run_command(f"samtools faidx {input_fasta}", "Indexing FASTA")
    
    # Extract regions
    region_args = " ".join(regions)
    cmd = f"samtools faidx {input_fasta} {region_args} > {output_fasta}"
    run_command(cmd, f"Extracting regions: {', '.join(regions)}")
    
    # Create index for output FASTA
    run_command(f"samtools faidx {output_fasta}", "Indexing output FASTA")
    
    return output_fasta

def get_chromosome_info(fasta_file):
    """Get chromosome information from FASTA index"""
    fai_file = f"{fasta_file}.fai"
    
    if not os.path.exists(fai_file):
        print(f"Creating FASTA index for {fasta_file}...")
        run_command(f"samtools faidx {fasta_file}", "Indexing FASTA")
    
    print(f"\nChromosome information from {fasta_file}:")
    with open(fai_file, 'r') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 2:
                chrom, length = parts[0], parts[1]
                if chrom.startswith('chr'):
                    print(f"  {chrom}: {length} bp")

def main():
    parser = argparse.ArgumentParser(description='Generate test reference FASTA from GRCh38')
    parser.add_argument('--input', '-i', 
                       default='/cbio/dbs/references/GRCh38_reference_genome/GRCh38_full_analysis_set_plus_decoy_hla.fa',
                       help='Input GRCh38 FASTA file')
    parser.add_argument('--output', '-o',
                       default='dev_docs/test_data/GRCh38_test_reference.fa',
                       help='Output test FASTA file')
    parser.add_argument('--chromosomes', '-c',
                       default='chr21,chr22',
                       help='Comma-separated list of chromosomes to extract')
    parser.add_argument('--regions', '-r',
                       help='Specific regions to extract (e.g., chr22:16000000-17000000)')
    parser.add_argument('--info-only', action='store_true',
                       help='Only show chromosome information, do not extract')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("GRCh38 Test Reference Generator")
    print("=" * 60)
    
    # Check dependencies
    check_dependencies()
    
    # Show chromosome information
    if os.path.exists(args.input):
        get_chromosome_info(args.input)
    else:
        print(f"Error: Input FASTA not found: {args.input}")
        sys.exit(1)
    
    if args.info_only:
        print("\nInfo-only mode. Exiting.")
        return
    
    # Prepare output directory
    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Determine regions to extract
    if args.regions:
        regions = [r.strip() for r in args.regions.split(',')]
    else:
        # Extract full chromosomes
        chromosomes = [c.strip() for c in args.chromosomes.split(',')]
        regions = chromosomes
    
    print(f"\nExtracting regions: {', '.join(regions)}")
    print(f"Output file: {args.output}")
    
    # Extract regions
    extract_chromosome_regions(args.input, args.output, regions)
    
    # Show output information
    print(f"\n✅ Test reference FASTA created: {args.output}")
    get_chromosome_info(args.output)
    
    # Calculate file sizes
    input_size = os.path.getsize(args.input) / (1024**3)  # GB
    output_size = os.path.getsize(args.output) / (1024**2)  # MB
    
    print(f"\nFile sizes:")
    print(f"  Input:  {input_size:.2f} GB")
    print(f"  Output: {output_size:.2f} MB")
    print(f"  Reduction: {(1 - output_size/(input_size*1024))*100:.1f}%")
    
    print(f"\n🎉 Test reference generation complete!")
    print(f"Use with: --target_fasta {os.path.abspath(args.output)}")

if __name__ == "__main__":
    main()
