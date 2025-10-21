#!/usr/bin/env python3

"""
VCF Validation Script
======================
Comprehensive VCF file validation for the liftover pipeline
"""

import argparse
import sys
import os
import gzip
import re
import subprocess
from pathlib import Path

def run_command(cmd):
    """Run a command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)

def check_file_format(vcf_file):
    """Check if file is a valid VCF format"""
    errors = []
    warnings = []
    
    # Check file extension
    if not vcf_file.endswith(('.vcf', '.vcf.gz', '.bcf')):
        errors.append(f"Invalid file extension: {vcf_file}")
        return errors, warnings
    
    # Check if file exists and is readable
    if not os.path.exists(vcf_file):
        errors.append(f"File not found: {vcf_file}")
        return errors, warnings
    
    try:
        # Open file (handle compressed files)
        if vcf_file.endswith('.gz'):
            file_handle = gzip.open(vcf_file, 'rt')
        else:
            file_handle = open(vcf_file, 'r')
        
        # Read first few lines
        lines = []
        for i, line in enumerate(file_handle):
            lines.append(line.strip())
            if i >= 100:  # Read first 100 lines
                break
        
        file_handle.close()
        
        # Check VCF header
        if not lines or not lines[0].startswith('##fileformat=VCF'):
            errors.append("Missing or invalid VCF header")
        
        # Check for required header lines
        header_found = False
        for line in lines:
            if line.startswith('#CHROM'):
                header_found = True
                break
        
        if not header_found:
            errors.append("Missing VCF column header line (#CHROM...)")
        
        # Check for data lines
        data_lines = [line for line in lines if not line.startswith('#') and line.strip()]
        if not data_lines:
            warnings.append("No data lines found in VCF file")
        else:
            # Validate first data line format
            first_data = data_lines[0].split('\t')
            if len(first_data) < 8:
                errors.append("Invalid VCF data line format (less than 8 columns)")
        
    except Exception as e:
        errors.append(f"Error reading file: {e}")
    
    return errors, warnings

def check_with_bcftools(vcf_file):
    """Validate VCF using bcftools"""
    errors = []
    warnings = []
    stats = {}
    
    # Check if bcftools is available
    returncode, stdout, stderr = run_command("which bcftools")
    if returncode != 0:
        warnings.append("bcftools not available for validation")
        return errors, warnings, stats
    
    # Validate header
    returncode, stdout, stderr = run_command(f"bcftools view -h {vcf_file}")
    if returncode != 0:
        errors.append(f"bcftools header validation failed: {stderr}")
        return errors, warnings, stats
    
    # Count variants
    returncode, stdout, stderr = run_command(f"bcftools view -H {vcf_file} | wc -l")
    if returncode == 0:
        try:
            stats['variant_count'] = int(stdout.strip())
        except ValueError:
            warnings.append("Could not count variants")
    
    # Get sample count
    returncode, stdout, stderr = run_command(f"bcftools query -l {vcf_file} | wc -l")
    if returncode == 0:
        try:
            stats['sample_count'] = int(stdout.strip())
        except ValueError:
            warnings.append("Could not count samples")
    
    # Check chromosomes
    returncode, stdout, stderr = run_command(f"bcftools view -H {vcf_file} | cut -f1 | sort | uniq")
    if returncode == 0:
        chromosomes = stdout.strip().split('\n')
        stats['chromosomes'] = [chr for chr in chromosomes if chr.strip()]
        stats['chromosome_count'] = len(stats['chromosomes'])
    
    # Validate VCF format more thoroughly
    returncode, stdout, stderr = run_command(f"bcftools view {vcf_file} -o /dev/null")
    if returncode != 0:
        errors.append(f"bcftools format validation failed: {stderr}")
    
    return errors, warnings, stats

def validate_coordinates(vcf_file, build=None):
    """Validate coordinate ranges for specific genome build"""
    errors = []
    warnings = []
    
    # Define chromosome length limits for common builds
    chr_limits = {
        'hg19': {
            '1': 249250621, '2': 242193529, '3': 198295559, '4': 191154276,
            '5': 180915260, '6': 171115067, '7': 159138663, '8': 146364022,
            '9': 141213431, '10': 135534747, '11': 135006516, '12': 133851895,
            '13': 115169878, '14': 107349540, '15': 102531392, '16': 90354753,
            '17': 81195210, '18': 78077248, '19': 59128983, '20': 63025520,
            '21': 48129895, '22': 51304566, 'X': 155270560, 'Y': 59373566,
            'MT': 16569
        },
        'hg38': {
            '1': 248956422, '2': 242193529, '3': 198295559, '4': 190214555,
            '5': 181538259, '6': 170805979, '7': 159345973, '8': 145138636,
            '9': 138394717, '10': 133797422, '11': 135086622, '12': 133275309,
            '13': 114364328, '14': 107043718, '15': 101991189, '16': 90338345,
            '17': 83257441, '18': 80373285, '19': 58617616, '20': 64444167,
            '21': 46709983, '22': 50818468, 'X': 156040895, 'Y': 57227415,
            'MT': 16569
        }
    }
    
    if not build or build not in chr_limits:
        warnings.append(f"Coordinate validation skipped (build: {build})")
        return errors, warnings
    
    limits = chr_limits[build]
    
    try:
        # Check coordinates using bcftools
        returncode, stdout, stderr = run_command(f"bcftools query -f '%CHROM\\t%POS\\n' {vcf_file}")
        if returncode != 0:
            warnings.append("Could not extract coordinates for validation")
            return errors, warnings
        
        invalid_coords = []
        for line in stdout.strip().split('\n')[:1000]:  # Check first 1000 variants
            if not line.strip():
                continue
            
            parts = line.strip().split('\t')
            if len(parts) >= 2:
                chrom = parts[0].replace('chr', '')  # Remove chr prefix if present
                try:
                    pos = int(parts[1])
                    if chrom in limits and pos > limits[chrom]:
                        invalid_coords.append(f"{chrom}:{pos}")
                except ValueError:
                    continue
        
        if invalid_coords:
            errors.append(f"Invalid coordinates found: {invalid_coords[:5]}")  # Show first 5
            
    except Exception as e:
        warnings.append(f"Coordinate validation error: {e}")
    
    return errors, warnings

def main():
    parser = argparse.ArgumentParser(description='Validate VCF files')
    parser.add_argument('vcf_file', help='VCF file to validate')
    parser.add_argument('--build', help='Genome build for coordinate validation (hg19, hg38)')
    parser.add_argument('--output', help='Output validation report file')
    parser.add_argument('--strict', action='store_true', help='Strict validation (warnings become errors)')
    
    args = parser.parse_args()
    
    print(f"Validating VCF file: {args.vcf_file}")
    
    all_errors = []
    all_warnings = []
    all_stats = {}
    
    # File format validation
    print("1. Checking file format...")
    errors, warnings = check_file_format(args.vcf_file)
    all_errors.extend(errors)
    all_warnings.extend(warnings)
    
    # bcftools validation
    print("2. Running bcftools validation...")
    errors, warnings, stats = check_with_bcftools(args.vcf_file)
    all_errors.extend(errors)
    all_warnings.extend(warnings)
    all_stats.update(stats)
    
    # Coordinate validation
    if args.build:
        print(f"3. Validating coordinates for {args.build}...")
        errors, warnings = validate_coordinates(args.vcf_file, args.build)
        all_errors.extend(errors)
        all_warnings.extend(warnings)
    
    # Generate report
    report_lines = []
    report_lines.append(f"VCF Validation Report: {args.vcf_file}")
    report_lines.append("=" * 60)
    
    if all_stats:
        report_lines.append("Statistics:")
        for key, value in all_stats.items():
            if key == 'chromosomes':
                report_lines.append(f"  {key}: {', '.join(value[:10])}")  # Show first 10
            else:
                report_lines.append(f"  {key}: {value}")
        report_lines.append("")
    
    if all_warnings:
        report_lines.append("Warnings:")
        for warning in all_warnings:
            report_lines.append(f"  - {warning}")
        report_lines.append("")
    
    if all_errors:
        report_lines.append("Errors:")
        for error in all_errors:
            report_lines.append(f"  - {error}")
        report_lines.append("")
    
    # Determine validation result
    if args.strict:
        validation_passed = len(all_errors) == 0 and len(all_warnings) == 0
    else:
        validation_passed = len(all_errors) == 0
    
    if validation_passed:
        report_lines.append("VALIDATION: PASSED")
        print("✓ Validation PASSED")
    else:
        report_lines.append("VALIDATION: FAILED")
        print("✗ Validation FAILED")
    
    # Write report
    if args.output:
        with open(args.output, 'w') as f:
            f.write('\n'.join(report_lines))
        print(f"Report written to: {args.output}")
    else:
        print('\n'.join(report_lines))
    
    # Exit with appropriate code
    sys.exit(0 if validation_passed else 1)

if __name__ == "__main__":
    main()
