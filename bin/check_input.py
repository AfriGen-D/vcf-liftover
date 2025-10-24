#!/usr/bin/env python3
"""
Input CSV Validation Script
Validates input CSV file and checks VCF file existence

Enhanced with checkref-inspired validation:
- File size validation (detect empty/corrupted files)
- Gzip integrity testing
- bcftools format validation
- Non-empty data check
- Visual error formatting
- Validation status files for graceful workflow continuation
"""

import csv
import sys
import os
import argparse
import subprocess
import gzip

# Import error formatting utility
try:
    from format_error_message import format_critical_error, format_warning, format_info
except ImportError:
    # Fallback if import fails (shouldn't happen in same directory)
    def format_critical_error(title, message_lines, suggestions=None):
        return f"ERROR: {title}\n" + "\n".join(message_lines if isinstance(message_lines, list) else [message_lines])
    def format_warning(title, message_lines, context=None):
        return f"WARNING: {title}\n" + "\n".join(message_lines if isinstance(message_lines, list) else [message_lines])
    def format_info(title, message_lines):
        return f"INFO: {title}\n" + "\n".join(message_lines if isinstance(message_lines, list) else [message_lines])


def run_command(cmd):
    """Run shell command and return status, stdout, stderr"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out"
    except Exception as e:
        return 1, "", str(e)


def check_file_size(vcf_path, sample_id):
    """Check if file size is reasonable (not empty or too small)"""
    try:
        file_size = os.path.getsize(vcf_path)

        if file_size == 0:
            error_msg = format_critical_error(
                title="Empty VCF File",
                message_lines=[
                    f"Sample: {sample_id}",
                    f"File: {vcf_path}",
                    "File size: 0 bytes"
                ],
                suggestions=[
                    "Check if file was created correctly",
                    "Verify file was not truncated during transfer",
                    "Re-download or regenerate the file"
                ]
            )
            return False, error_msg

        elif file_size < 100:
            warning_msg = format_warning(
                title="Very Small File Detected",
                message_lines=[
                    f"Sample: {sample_id}",
                    f"File: {vcf_path}",
                    f"File size: {file_size} bytes"
                ],
                context="File may be corrupted or contain only headers. Will attempt validation."
            )
            print(warning_msg, file=sys.stderr)
            # Continue with validation (warning, not error)

        return True, None

    except Exception as e:
        error_msg = format_critical_error(
            title="Cannot Check File Size",
            message_lines=[
                f"Sample: {sample_id}",
                f"File: {vcf_path}",
                f"Error: {e}"
            ],
            suggestions=["Check file permissions: ls -l " + vcf_path]
        )
        return False, error_msg


def check_gzip_integrity(vcf_path, sample_id):
    """Test gzip file integrity (prevents crashes later in pipeline)"""
    if not vcf_path.endswith('.gz'):
        return True, None  # Not gzipped, skip check

    returncode, stdout, stderr = run_command(f"gunzip -t '{vcf_path}'")

    if returncode != 0:
        error_msg = format_critical_error(
            title="Corrupted Gzip File",
            message_lines=[
                f"Sample: {sample_id}",
                f"File: {vcf_path}",
                "Gzip integrity test failed",
                f"Error: {stderr.strip() if stderr else 'gunzip test failed'}"
            ],
            suggestions=[
                "Re-download the file",
                "Re-compress with: bgzip -c original.vcf > output.vcf.gz",
                "Verify file integrity: gunzip -t " + vcf_path
            ]
        )
        return False, error_msg

    return True, None


def check_vcf_format(vcf_path, sample_id):
    """Validate VCF format using bcftools"""
    # Check if bcftools is available
    returncode, _, _ = run_command("which bcftools")
    if returncode != 0:
        print(format_warning(
            title="bcftools Not Available",
            message_lines=["Skipping detailed VCF format validation"],
            context="Install bcftools for comprehensive validation"
        ), file=sys.stderr)
        return True, None  # Not a failure, just skip this check

    # Try to read VCF header
    returncode, stdout, stderr = run_command(f"bcftools view -h '{vcf_path}' 2>&1 | head -1")

    if returncode != 0:
        error_msg = format_critical_error(
            title="Invalid VCF Format",
            message_lines=[
                f"Sample: {sample_id}",
                f"File: {vcf_path}",
                "bcftools cannot read VCF header",
                f"Error: {stderr.strip() if stderr else 'Format validation failed'}"
            ],
            suggestions=[
                "Validate VCF format: bcftools view -h " + vcf_path,
                "Check if file is truly a VCF file",
                "Verify VCF header starts with ##fileformat=VCF"
            ]
        )
        return False, error_msg

    return True, None


def check_vcf_has_data(vcf_path, sample_id):
    """Check if VCF has at least one variant (not just headers)"""
    # Check if bcftools is available
    returncode, _, _ = run_command("which bcftools")
    if returncode != 0:
        return True, None  # Skip if bcftools not available

    # Count variant lines (non-header lines)
    returncode, stdout, stderr = run_command(f"bcftools view -H '{vcf_path}' | head -1")

    if returncode == 0 and stdout.strip():
        return True, None  # Has data

    # No data found - this is a warning, not necessarily an error
    warning_msg = format_warning(
        title="VCF File Has No Variants",
        message_lines=[
            f"Sample: {sample_id}",
            f"File: {vcf_path}",
            "File has valid header but no variant data"
        ],
        context="This may be expected if file represents an empty result after filtering"
    )
    print(warning_msg, file=sys.stderr)
    return True, None  # Continue (warning only)


def validate_single_vcf(sample_id, vcf_path):
    """
    Comprehensive validation for a single VCF file.
    Returns (is_valid, error_message, status)
    """
    print(f"\nValidating sample: {sample_id}")
    print(f"  File: {vcf_path}")

    # Check 1: File existence
    if not os.path.exists(vcf_path):
        error_msg = format_critical_error(
            title="VCF File Not Found",
            message_lines=[
                f"Sample: {sample_id}",
                f"Expected path: {vcf_path}",
                f"Current directory: {os.getcwd()}"
            ],
            suggestions=[
                "Check if the file path is correct",
                "Verify the file exists: ls -la " + vcf_path,
                "Use absolute paths instead of relative paths"
            ]
        )
        return False, error_msg, "FAILED"

    # Check 2: File extension
    valid_extensions = ('.vcf', '.vcf.gz', '.bcf')
    if not vcf_path.endswith(valid_extensions):
        error_msg = format_critical_error(
            title="Invalid VCF File Extension",
            message_lines=[
                f"Sample: {sample_id}",
                f"File: {vcf_path}",
                f"Expected extensions: {valid_extensions}"
            ],
            suggestions=["Ensure file has .vcf, .vcf.gz, or .bcf extension"]
        )
        return False, error_msg, "FAILED"

    # Check 3: File is readable
    try:
        with open(vcf_path, 'rb') as test_file:
            test_file.read(1)
    except IOError as e:
        error_msg = format_critical_error(
            title="Cannot Read VCF File",
            message_lines=[
                f"Sample: {sample_id}",
                f"File: {vcf_path}",
                f"Error: {e}"
            ],
            suggestions=[
                "Check file permissions: ls -l " + vcf_path,
                "Ensure file is not being written by another process"
            ]
        )
        return False, error_msg, "FAILED"

    # Check 4: File size
    is_valid, error_msg = check_file_size(vcf_path, sample_id)
    if not is_valid:
        return False, error_msg, "FAILED"

    # Check 5: Gzip integrity (if compressed)
    is_valid, error_msg = check_gzip_integrity(vcf_path, sample_id)
    if not is_valid:
        return False, error_msg, "FAILED"

    # Check 6: VCF format validation
    is_valid, error_msg = check_vcf_format(vcf_path, sample_id)
    if not is_valid:
        return False, error_msg, "FAILED"

    # Check 7: Has variant data (warning only)
    check_vcf_has_data(vcf_path, sample_id)

    print(f"  ✓ All validation checks passed for {sample_id}")
    return True, None, "PASSED"


def validate_input(input_file, output_file):
    """Validate input CSV and write validated output"""
    validated_samples = []
    failed_samples = []

    with open(input_file, 'r') as f:
        reader = csv.DictReader(f)

        # Check required columns
        required_cols = ['sample_id', 'vcf_path']
        if not all(col in reader.fieldnames for col in required_cols):
            error_msg = format_critical_error(
                title="Invalid CSV Format",
                message_lines=[
                    f"Input CSV: {input_file}",
                    f"Required columns: {required_cols}",
                    f"Found columns: {reader.fieldnames}"
                ],
                suggestions=[
                    "Ensure CSV has 'sample_id' and 'vcf_path' columns",
                    "Check CSV header row is correct"
                ]
            )
            print(error_msg, file=sys.stderr)
            sys.exit(1)

        for row in reader:
            sample_id = row['sample_id']
            vcf_path = row['vcf_path']

            # Check if sample_id is provided
            if not sample_id or sample_id.strip() == '':
                error_msg = format_critical_error(
                    title="Empty Sample ID",
                    message_lines=[
                        "Found row with empty sample_id",
                        f"Row data: {row}"
                    ],
                    suggestions=["Ensure all rows have a sample_id value"]
                )
                print(error_msg, file=sys.stderr)
                sys.exit(1)

            # Check if VCF path is provided
            if not vcf_path or vcf_path.strip() == '':
                error_msg = format_critical_error(
                    title="Empty VCF Path",
                    message_lines=[
                        f"Sample: {sample_id}",
                        "vcf_path is empty"
                    ],
                    suggestions=["Ensure all rows have a vcf_path value"]
                )
                print(error_msg, file=sys.stderr)
                sys.exit(1)

            # Comprehensive VCF validation
            is_valid, error_msg, status = validate_single_vcf(sample_id, vcf_path)

            # Write validation status file for workflow filtering
            status_file = f"{sample_id}_validation_status.txt"
            with open(status_file, 'w') as sf:
                sf.write(status)

            if is_valid:
                validated_samples.append({'sample_id': sample_id, 'vcf_path': vcf_path})
            else:
                print(error_msg, file=sys.stderr)
                failed_samples.append(sample_id)
                # Write detailed error report
                with open(f"{sample_id}_validation_error.txt", 'w') as ef:
                    ef.write(error_msg)

    # Check for duplicate sample IDs
    sample_ids = [sample['sample_id'] for sample in validated_samples]
    duplicates = set([x for x in sample_ids if sample_ids.count(x) > 1])
    if duplicates:
        error_msg = format_critical_error(
            title="Duplicate Sample IDs",
            message_lines=[
                "Found duplicate sample IDs in input CSV:",
                *[f"  - {dup}" for dup in duplicates]
            ],
            suggestions=["Ensure each sample has a unique sample_id"]
        )
        print(error_msg, file=sys.stderr)
        sys.exit(1)

    # Summary
    total_samples = len(validated_samples) + len(failed_samples)

    if failed_samples:
        print(format_warning(
            title="Validation Complete with Failures",
            message_lines=[
                f"Total samples: {total_samples}",
                f"Passed: {len(validated_samples)}",
                f"Failed: {len(failed_samples)}",
                "",
                "Failed samples:",
                *[f"  ❌ {sample}" for sample in failed_samples],
                "",
                "Failed samples will be skipped in the workflow.",
                "Check *_validation_error.txt files for details."
            ]
        ), file=sys.stderr)

        if len(validated_samples) == 0:
            # All samples failed - exit with error
            error_msg = format_critical_error(
                title="All Samples Failed Validation",
                message_lines=[
                    f"Validated: 0/{total_samples}",
                    "Cannot proceed with workflow"
                ],
                suggestions=[
                    "Fix validation errors in input files",
                    "Check *_validation_error.txt files for details"
                ]
            )
            print(error_msg, file=sys.stderr)
            sys.exit(1)
    else:
        # All samples passed
        print(format_info(
            title="Validation Complete",
            message_lines=[
                f"✓ All {len(validated_samples)} samples passed validation",
                "Ready to proceed with liftover workflow"
            ]
        ))

    # Write validated samples (even if some failed, write the valid ones)
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['sample_id', 'vcf_path'])
        writer.writeheader()
        writer.writerows(validated_samples)

    # Print summary
    print(f"\nValidated samples ({len(validated_samples)}):")
    for sample in validated_samples:
        file_size = os.path.getsize(sample['vcf_path'])
        print(f"  ✓ {sample['sample_id']}: {sample['vcf_path']} ({file_size:,} bytes)")


def main():
    parser = argparse.ArgumentParser(description='Validate input CSV file')
    parser.add_argument('--input', required=True, help='Input CSV file')
    parser.add_argument('--output', required=True, help='Output validated CSV file')

    args = parser.parse_args()

    validate_input(args.input, args.output)


if __name__ == "__main__":
    main()
