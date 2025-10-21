#!/usr/bin/env python3
"""
Chromosome Compatibility Validation Script

Checks if chromosomes in VCF files exist in the target reference genome.
Detects common issues like:
- Wrong reference genome (e.g., using chr22 when data has chr4/8/9)
- Chromosome naming mismatches (e.g., "4" vs "chr4")
"""

import csv
import sys
import gzip
import argparse
from pathlib import Path


def get_vcf_chromosomes(vcf_path):
    """Extract chromosome names from VCF header"""
    chromosomes = set()

    # Check if file is gzipped
    if vcf_path.endswith('.gz'):
        opener = gzip.open
        mode = 'rt'
    else:
        opener = open
        mode = 'r'

    with opener(vcf_path, mode) as f:
        for line in f:
            if line.startswith('##contig=<ID='):
                # Extract chromosome from ##contig=<ID=chr1,...>
                chrom = line.split('ID=')[1].split(',')[0].split('>')[0]
                chromosomes.add(chrom)
            elif line.startswith('#CHROM'):
                # Header line found, stop reading
                break
            elif not line.startswith('#'):
                # Data line reached without finding contigs in header
                # Extract from first data line
                chrom = line.split('\t')[0]
                chromosomes.add(chrom)
                break

    return chromosomes


def get_reference_chromosomes(fasta_path):
    """Extract chromosome names from FASTA index file"""
    chromosomes = set()
    fai_path = f"{fasta_path}.fai"

    if not Path(fai_path).exists():
        sys.exit(f"ERROR: FASTA index file not found: {fai_path}\n"
                 f"Please create it with: samtools faidx {fasta_path}")

    with open(fai_path, 'r') as f:
        for line in f:
            chrom = line.split('\t')[0]
            chromosomes.add(chrom)

    return chromosomes


def normalize_chromosome(chrom):
    """Remove or add 'chr' prefix for comparison"""
    if chrom.startswith('chr'):
        return chrom[3:]
    else:
        return chrom


def check_chromosome_compatibility(vcf_chromosomes, ref_chromosomes, sample_id, vcf_path):
    """Check if VCF chromosomes exist in reference, with helpful error messages"""

    # Direct matches
    matching = vcf_chromosomes & ref_chromosomes
    missing = vcf_chromosomes - ref_chromosomes

    if not missing:
        # All chromosomes match - perfect!
        return True, None

    # Check if it's a naming convention mismatch (chr prefix)
    missing_normalized = {normalize_chromosome(c) for c in missing}
    ref_normalized = {normalize_chromosome(c) for c in ref_chromosomes}

    # Check if chromosomes would match with/without 'chr' prefix
    naming_mismatch = missing_normalized & ref_normalized
    completely_missing = missing_normalized - ref_normalized

    # IMPORTANT: If it's only a naming mismatch (chr vs no-chr), this is OK for liftover!
    # The chain file handles chromosome name changes between genome builds.
    # Only fail if chromosomes are completely missing from the reference.
    if naming_mismatch and not completely_missing:
        # This is just a naming convention difference - CrossMap will handle it
        print(f"\nℹ INFO: Naming convention difference detected for sample: {sample_id}")
        print(f"  VCF chromosomes: {sorted(missing)}")
        print(f"  Reference has equivalent chromosomes with different naming")
        print(f"  → CrossMap will handle chromosome name mapping via the chain file")
        return True, None  # Not an error!

    if not completely_missing:
        # All chromosomes exist (with or without name differences)
        return True, None

    # Build error message for completely missing chromosomes
    errors = []
    errors.append(f"\nERROR: Chromosome mismatch detected for sample: {sample_id}")
    errors.append(f"VCF file: {vcf_path}")
    errors.append(f"\nVCF chromosomes: {sorted(vcf_chromosomes)}")
    errors.append(f"Reference chromosomes: {sorted(ref_chromosomes)}")

    if matching:
        errors.append(f"\n✓ Matching chromosomes: {sorted(matching)}")

    # Only report completely missing chromosomes as errors
    errors.append(f"\n✗ These chromosomes are completely missing from the reference:")
    errors.append(f"  {sorted(completely_missing)}")
    errors.append(f"\nSuggestion:")
    errors.append(f"  • You are using the WRONG reference genome!")
    errors.append(f"  • Your data has chromosomes: {sorted(completely_missing)}")
    errors.append(f"  • But the reference only has: {sorted(ref_normalized)}")
    errors.append(f"  • Please provide a reference genome that contains all chromosomes in your data")

    return False, '\n'.join(errors)


def validate_all_samples(input_csv, target_fasta):
    """Validate chromosome compatibility for all samples"""

    print(f"Validating chromosome compatibility...")
    print(f"Target reference: {target_fasta}")

    # Get reference chromosomes
    ref_chromosomes = get_reference_chromosomes(target_fasta)
    print(f"Reference contains {len(ref_chromosomes)} chromosome(s): {sorted(ref_chromosomes)}")

    # Read samples
    with open(input_csv, 'r') as f:
        reader = csv.DictReader(f)
        samples = list(reader)

    # Validate each sample
    all_valid = True
    for sample in samples:
        sample_id = sample['sample_id']
        vcf_path = sample['vcf_path']

        print(f"\nChecking sample: {sample_id}")

        # Get VCF chromosomes
        vcf_chromosomes = get_vcf_chromosomes(vcf_path)
        print(f"  VCF chromosomes: {sorted(vcf_chromosomes)}")

        # Check compatibility
        is_valid, error_msg = check_chromosome_compatibility(
            vcf_chromosomes, ref_chromosomes, sample_id, vcf_path
        )

        if not is_valid:
            print(error_msg)
            all_valid = False
        else:
            print(f"  ✓ All chromosomes are compatible")

    if not all_valid:
        sys.exit(1)

    print(f"\n✓ All samples passed chromosome validation!")


def main():
    parser = argparse.ArgumentParser(
        description='Validate chromosome compatibility between VCF files and reference genome'
    )
    parser.add_argument('--input', required=True, help='Input CSV file with sample_id,vcf_path')
    parser.add_argument('--target-fasta', required=True, help='Target reference genome FASTA')

    args = parser.parse_args()

    validate_all_samples(args.input, args.target_fasta)


if __name__ == "__main__":
    main()
