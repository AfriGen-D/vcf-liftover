#!/usr/bin/env python3
"""
Chromosome Compatibility Validation Script

Checks if chromosomes in VCF files exist in the target reference genome.
Detects common issues like:
- Wrong reference genome (e.g., using chr22 when data has chr4/8/9)
- Chromosome naming mismatches (e.g., "4" vs "chr4")

Enhanced with visual error formatting and detailed suggestions.
"""

import csv
import sys
import gzip
import argparse
from pathlib import Path

# Import error formatting
try:
    from format_error_message import format_critical_error, format_info, format_warning
except ImportError:
    # Fallback
    def format_critical_error(title, msgs, suggestions=None):
        return f"ERROR: {title}\n" + "\n".join(msgs if isinstance(msgs, list) else [msgs])
    def format_info(title, msgs):
        return f"INFO: {title}\n" + "\n".join(msgs if isinstance(msgs, list) else [msgs])
    def format_warning(title, msgs, ctx=None):
        return f"WARNING: {title}\n" + "\n".join(msgs if isinstance(msgs, list) else [msgs])


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
        info_msg = format_info(
            title="Chromosome Naming Difference Detected",
            message_lines=[
                f"Sample: {sample_id}",
                f"VCF uses: {', '.join(sorted(missing)[:5])}{'...' if len(missing) > 5 else ''}",
                f"Reference uses different naming convention",
                "",
                "✓ This is OK! CrossMap will handle chromosome name mapping via the chain file."
            ]
        )
        print(info_msg)
        return True, None  # Not an error!

    if not completely_missing:
        # All chromosomes exist (with or without name differences)
        return True, None

    # Build error message for completely missing chromosomes
    error_msg = format_critical_error(
        title="Chromosome Mismatch - Wrong Reference Genome",
        message_lines=[
            f"Sample: {sample_id}",
            f"VCF file: {vcf_path}",
            "",
            f"VCF chromosomes: {', '.join(sorted(vcf_chromosomes))}",
            f"Reference chromosomes: {', '.join(sorted(ref_chromosomes))}",
            "",
            "✓ Matching chromosomes: " + (', '.join(sorted(matching)) if matching else "NONE"),
            "❌ Missing from reference: " + ', '.join(sorted(completely_missing)),
            "",
            "Your VCF contains chromosomes that are NOT in the target reference genome.",
            "This means you are using the WRONG reference genome!"
        ],
        suggestions=[
            f"Your data has chromosomes: {', '.join(sorted(completely_missing)[:5])}",
            f"But the reference only has: {', '.join(sorted(ref_normalized)[:10])}",
            "Provide a reference genome that contains ALL chromosomes in your VCF",
            "Check if you're mixing chromosome subsets (e.g., chr22 ref with whole-genome VCF)"
        ]
    )

    return False, error_msg


def validate_all_samples(input_csv, target_fasta):
    """Validate chromosome compatibility for all samples"""

    print(format_info(
        title="Chromosome Validation Starting",
        message_lines=[
            f"Target reference: {target_fasta}",
            "Checking if VCF chromosomes exist in reference genome..."
        ]
    ))

    # Get reference chromosomes
    ref_chromosomes = get_reference_chromosomes(target_fasta)
    print(f"\nReference contains {len(ref_chromosomes)} chromosome(s):")
    print(f"  {', '.join(sorted(ref_chromosomes)[:15])}{'...' if len(ref_chromosomes) > 15 else ''}")

    # Read samples
    with open(input_csv, 'r') as f:
        reader = csv.DictReader(f)
        samples = list(reader)

    # Validate each sample
    all_valid = True
    for sample in samples:
        sample_id = sample['sample_id']
        vcf_path = sample['vcf_path']

        print(f"\n{'─' * 76}")
        print(f"Checking sample: {sample_id}")

        # Get VCF chromosomes
        vcf_chromosomes = get_vcf_chromosomes(vcf_path)
        print(f"  VCF chromosomes: {', '.join(sorted(vcf_chromosomes))}")

        # Check compatibility
        is_valid, error_msg = check_chromosome_compatibility(
            vcf_chromosomes, ref_chromosomes, sample_id, vcf_path
        )

        if not is_valid:
            print(error_msg, file=sys.stderr)
            all_valid = False
        else:
            print(f"  ✓ All chromosomes are compatible")

    print(f"\n{'═' * 76}")

    if not all_valid:
        print(format_critical_error(
            title="Chromosome Validation Failed",
            message_lines=[
                "One or more samples have chromosomes missing from the target reference",
                "Cannot proceed with liftover"
            ],
            suggestions=[
                "Check error messages above for specific missing chromosomes",
                "Ensure you're using the correct target reference genome",
                "Verify reference contains all chromosomes in your VCF files"
            ]
        ), file=sys.stderr)
        sys.exit(1)

    print(format_info(
        title="Chromosome Validation Complete",
        message_lines=[
            f"✓ All {len(samples)} samples passed validation",
            "All VCF chromosomes are present in the target reference",
            "Ready to proceed with liftover"
        ]
    ))


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
