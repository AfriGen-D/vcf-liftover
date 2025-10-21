#!/usr/bin/env python3
"""
Input CSV Validation Script
Validates input CSV file and checks VCF file existence
"""

import csv
import sys
import os
import argparse


def validate_input(input_file, output_file):
    """Validate input CSV and write validated output"""
    validated_samples = []

    with open(input_file, 'r') as f:
        reader = csv.DictReader(f)

        # Check required columns
        required_cols = ['sample_id', 'vcf_path']
        if not all(col in reader.fieldnames for col in required_cols):
            sys.exit(f"ERROR: Input CSV must contain columns: {required_cols}")

        for row in reader:
            sample_id = row['sample_id']
            vcf_path = row['vcf_path']

            # Check if sample_id is provided
            if not sample_id or sample_id.strip() == '':
                sys.exit(f"ERROR: Empty sample_id found in row: {row}")

            # Check if VCF path is provided
            if not vcf_path or vcf_path.strip() == '':
                sys.exit(f"ERROR: Empty vcf_path found for sample: {sample_id}")

            # Check if VCF file exists
            if not os.path.exists(vcf_path):
                sys.exit(f"ERROR: VCF file not found: {vcf_path}")

            # Check file extension
            valid_extensions = ('.vcf', '.vcf.gz', '.bcf')
            if not vcf_path.endswith(valid_extensions):
                sys.exit(f"ERROR: Invalid VCF file format: {vcf_path}. Must end with {valid_extensions}")

            # Check file is readable
            try:
                with open(vcf_path, 'rb') as test_file:
                    test_file.read(1)
            except IOError as e:
                sys.exit(f"ERROR: Cannot read VCF file {vcf_path}: {e}")

            validated_samples.append({'sample_id': sample_id, 'vcf_path': vcf_path})

    # Check for duplicate sample IDs
    sample_ids = [sample['sample_id'] for sample in validated_samples]
    duplicates = set([x for x in sample_ids if sample_ids.count(x) > 1])
    if duplicates:
        sys.exit(f"ERROR: Duplicate sample IDs found: {duplicates}")

    # Write validated samples
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['sample_id', 'vcf_path'])
        writer.writeheader()
        writer.writerows(validated_samples)

    print(f"Successfully validated {len(validated_samples)} samples")

    # Print summary
    for sample in validated_samples:
        print(f"  - {sample['sample_id']}: {sample['vcf_path']}")


def main():
    parser = argparse.ArgumentParser(description='Validate input CSV file')
    parser.add_argument('--input', required=True, help='Input CSV file')
    parser.add_argument('--output', required=True, help='Output validated CSV file')

    args = parser.parse_args()

    validate_input(args.input, args.output)


if __name__ == "__main__":
    main()
