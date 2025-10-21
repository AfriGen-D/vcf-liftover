#!/usr/bin/env python3
"""
VCF Validation Script
Validates output VCF files for format compliance and data integrity
"""

import subprocess
import sys
import os
import gzip
import argparse


def run_command(cmd):
    """Run a command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)


def validate_vcf(sample_id, vcf_file, index_file):
    """Comprehensive VCF validation"""

    report_lines = []
    report_lines.append(f"VCF Validation Report for Sample: {sample_id}")
    report_lines.append("=" * 60)
    report_lines.append(f"VCF File: {vcf_file}")
    report_lines.append(f"Index File: {index_file}")
    report_lines.append("")

    validation_passed = True

    # Check file existence
    report_lines.append("1. File Existence Check:")
    if not os.path.exists(vcf_file):
        report_lines.append(f"   FAIL: VCF file not found: {vcf_file}")
        validation_passed = False
    else:
        report_lines.append(f"   PASS: VCF file exists")

    if not os.path.exists(index_file):
        report_lines.append(f"   FAIL: Index file not found: {index_file}")
        validation_passed = False
    else:
        report_lines.append(f"   PASS: Index file exists")

    report_lines.append("")

    # Check file format
    report_lines.append("2. File Format Check:")
    if vcf_file.endswith('.gz'):
        try:
            with gzip.open(vcf_file, 'rt') as f:
                first_line = f.readline()
                if first_line.startswith('##fileformat=VCF'):
                    report_lines.append("   PASS: Valid VCF header format")
                else:
                    report_lines.append("   FAIL: Invalid VCF header format")
                    validation_passed = False
        except Exception as e:
            report_lines.append(f"   FAIL: Cannot read VCF file: {e}")
            validation_passed = False
    else:
        report_lines.append("   FAIL: VCF file is not compressed")
        validation_passed = False

    report_lines.append("")

    # Check with bcftools if available
    report_lines.append("3. bcftools Validation:")
    returncode, stdout, stderr = run_command(f"bcftools view -h {vcf_file}")
    if returncode == 0:
        report_lines.append("   PASS: bcftools can read VCF header")

        # Count variants
        returncode, stdout, stderr = run_command(f"bcftools view -H {vcf_file} | wc -l")
        if returncode == 0:
            variant_count = stdout.strip()
            report_lines.append(f"   INFO: Variant count: {variant_count}")

        # Check chromosomes
        returncode, stdout, stderr = run_command(f"bcftools view -H {vcf_file} | cut -f1 | sort | uniq -c")
        if returncode == 0:
            report_lines.append("   INFO: Chromosome distribution:")
            for line in stdout.strip().split('\n')[:10]:  # Show first 10 chromosomes
                if line.strip():
                    report_lines.append(f"     {line.strip()}")
    else:
        report_lines.append(f"   WARNING: bcftools not available: {stderr}")
        report_lines.append("   INFO: Skipping bcftools validation (not required for basic validation)")

    report_lines.append("")

    # Test index functionality
    report_lines.append("4. Index Functionality Test:")
    returncode, stdout, stderr = run_command(f"bcftools view {vcf_file} chr1:1-1000 2>/dev/null | head -1")
    if returncode == 0:
        report_lines.append("   PASS: Index allows region queries")
    else:
        # Try with different chromosome naming
        returncode, stdout, stderr = run_command(f"bcftools view {vcf_file} 1:1-1000 2>/dev/null | head -1")
        if returncode == 0:
            report_lines.append("   PASS: Index allows region queries")
        else:
            report_lines.append("   WARNING: Could not test region queries")

    report_lines.append("")

    # File size check
    report_lines.append("5. File Size Check:")
    try:
        vcf_size = os.path.getsize(vcf_file)
        index_size = os.path.getsize(index_file)
        report_lines.append(f"   INFO: VCF file size: {vcf_size:,} bytes")
        report_lines.append(f"   INFO: Index file size: {index_size:,} bytes")

        if vcf_size == 0:
            report_lines.append("   FAIL: VCF file is empty")
            validation_passed = False
        elif vcf_size < 100:
            report_lines.append("   WARNING: VCF file is very small")
        else:
            report_lines.append("   PASS: VCF file has reasonable size")

    except Exception as e:
        report_lines.append(f"   ERROR: Cannot check file sizes: {e}")

    report_lines.append("")
    report_lines.append("=" * 60)

    if validation_passed:
        report_lines.append("OVERALL RESULT: VALIDATION PASSED")
    else:
        report_lines.append("OVERALL RESULT: VALIDATION FAILED")

    report_lines.append("=" * 60)

    return validation_passed, report_lines


def main():
    parser = argparse.ArgumentParser(description='Validate VCF file')
    parser.add_argument('--sample-id', required=True, help='Sample ID')
    parser.add_argument('--vcf', required=True, help='VCF file path')
    parser.add_argument('--index', required=True, help='Index file path')
    parser.add_argument('--output', required=True, help='Output report file')

    args = parser.parse_args()

    print(f"Starting validation for sample: {args.sample_id}")

    validation_passed, report_lines = validate_vcf(args.sample_id, args.vcf, args.index)

    # Write report
    with open(args.output, "w") as f:
        f.write("\n".join(report_lines))

    # Print summary
    for line in report_lines:
        print(line)

    if not validation_passed:
        print(f"ERROR: Validation failed for sample {args.sample_id}")
        sys.exit(1)
    else:
        print(f"SUCCESS: Validation passed for sample {args.sample_id}")


if __name__ == "__main__":
    main()
