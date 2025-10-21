#!/usr/bin/env python3
"""
Generate chromosome mapping file based on VCF and reference naming conventions.

This script:
1. Detects chromosome naming in the input VCF (e.g., "1", "2", "X")
2. Detects chromosome naming in the target reference (e.g., "chr1", "chr2", "chrX")
3. Auto-generates a mapping file to convert from VCF naming to reference naming

Usage:
    generate_chr_mapping.py --vcf input.vcf --fai reference.fa.fai -o chr_mapping.txt
"""

import argparse
import sys
import gzip
from pathlib import Path


def open_vcf(vcf_path):
    """Open VCF file (handles both gzipped and plain text)."""
    if vcf_path.endswith('.gz'):
        return gzip.open(vcf_path, 'rt')
    return open(vcf_path, 'r')


def extract_vcf_chromosomes(vcf_path):
    """Extract chromosome names from VCF file."""
    chromosomes = set()

    with open_vcf(vcf_path) as f:
        for line in f:
            if line.startswith('#'):
                continue
            # First column is chromosome
            chrom = line.split('\t')[0]
            chromosomes.add(chrom)

            # Stop after we've seen enough unique chromosomes
            if len(chromosomes) >= 50:
                break

    return sorted(chromosomes)


def extract_reference_chromosomes(fai_path):
    """Extract chromosome names from FASTA index file."""
    chromosomes = []

    with open(fai_path, 'r') as f:
        for line in f:
            chrom = line.split('\t')[0]
            chromosomes.append(chrom)

    return chromosomes


def normalize_chrom(chrom):
    """Remove 'chr' prefix if present."""
    if chrom.startswith('chr'):
        return chrom[3:]
    return chrom


def has_chr_prefix(chromosomes):
    """Check if chromosomes use 'chr' prefix."""
    # Check first few chromosomes
    for chrom in chromosomes[:10]:
        if chrom.startswith('chr'):
            return True
    return False


def generate_mapping(vcf_chroms, ref_chroms):
    """
    Generate chromosome mapping from VCF naming to reference naming.

    Returns:
        List of tuples (vcf_chrom, ref_chrom) or None if no mapping needed
    """
    vcf_has_chr = has_chr_prefix(vcf_chroms)
    ref_has_chr = has_chr_prefix(ref_chroms)

    print(f"VCF chromosome naming: {'chr-prefixed' if vcf_has_chr else 'no prefix'}", file=sys.stderr)
    print(f"Reference chromosome naming: {'chr-prefixed' if ref_has_chr else 'no prefix'}", file=sys.stderr)

    # No mapping needed if both use same convention
    if vcf_has_chr == ref_has_chr:
        print("No chromosome renaming needed - both use same naming convention", file=sys.stderr)
        return None

    # Create normalized reference lookup
    ref_lookup = {}
    for ref_chrom in ref_chroms:
        normalized = normalize_chrom(ref_chrom)
        ref_lookup[normalized] = ref_chrom

    # Generate mappings
    mappings = []
    missing = []

    for vcf_chrom in vcf_chroms:
        normalized = normalize_chrom(vcf_chrom)

        if normalized in ref_lookup:
            ref_chrom = ref_lookup[normalized]
            if vcf_chrom != ref_chrom:
                mappings.append((vcf_chrom, ref_chrom))
        else:
            missing.append(vcf_chrom)

    if missing:
        print(f"\nWARNING: The following chromosomes from VCF are not in reference:", file=sys.stderr)
        for chrom in missing:
            print(f"  - {chrom}", file=sys.stderr)
        print("These will not be included in the mapping (they may be filtered by CrossMap)", file=sys.stderr)

    if not mappings:
        print("No chromosome renaming needed", file=sys.stderr)
        return None

    print(f"\nGenerated {len(mappings)} chromosome mappings:", file=sys.stderr)
    for old, new in mappings[:5]:
        print(f"  {old} → {new}", file=sys.stderr)
    if len(mappings) > 5:
        print(f"  ... and {len(mappings) - 5} more", file=sys.stderr)

    return mappings


def main():
    parser = argparse.ArgumentParser(
        description="Generate chromosome mapping file for VCF liftover"
    )
    parser.add_argument(
        '--vcf',
        required=True,
        help="Input VCF file (can be gzipped)"
    )
    parser.add_argument(
        '--fai',
        required=True,
        help="Target reference FASTA index file (.fai)"
    )
    parser.add_argument(
        '-o', '--output',
        required=True,
        help="Output chromosome mapping file"
    )

    args = parser.parse_args()

    # Validate inputs
    if not Path(args.vcf).exists():
        print(f"ERROR: VCF file not found: {args.vcf}", file=sys.stderr)
        sys.exit(1)

    if not Path(args.fai).exists():
        print(f"ERROR: FASTA index file not found: {args.fai}", file=sys.stderr)
        sys.exit(1)

    print(f"Analyzing chromosome naming...", file=sys.stderr)
    print(f"VCF file: {args.vcf}", file=sys.stderr)
    print(f"Reference index: {args.fai}", file=sys.stderr)

    # Extract chromosomes
    vcf_chroms = extract_vcf_chromosomes(args.vcf)
    ref_chroms = extract_reference_chromosomes(args.fai)

    print(f"\nFound {len(vcf_chroms)} chromosomes in VCF", file=sys.stderr)
    print(f"Found {len(ref_chroms)} chromosomes in reference", file=sys.stderr)

    # Generate mapping
    mappings = generate_mapping(vcf_chroms, ref_chroms)

    if mappings is None:
        # Create empty mapping file to indicate no mapping needed
        with open(args.output, 'w') as f:
            f.write("# No chromosome renaming needed\n")
        print(f"\nCreated empty mapping file: {args.output}", file=sys.stderr)
    else:
        # Write mapping file
        with open(args.output, 'w') as f:
            for old, new in mappings:
                f.write(f"{old}\t{new}\n")
        print(f"\nCreated mapping file: {args.output}", file=sys.stderr)

    print("✓ Chromosome mapping generation complete", file=sys.stderr)


if __name__ == '__main__':
    main()
