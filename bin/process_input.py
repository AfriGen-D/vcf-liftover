#!/usr/bin/env python3

import os
import csv
import sys
import glob
import argparse
from pathlib import Path

def is_vcf_file(filename):
    """Check if file is a VCF file"""
    return filename.lower().endswith(('.vcf', '.vcf.gz', '.bcf'))

def is_csv_file(filename):
    """Check if file is a CSV file"""
    return filename.lower().endswith('.csv')

def process_input(input_param, launch_dir=None):
    """Process different input types"""

    processed_samples = []

    print(f"Processing input: {input_param}")

    # Check if input contains wildcards or comma-separated files
    if '*' in input_param or '?' in input_param:
        # Handle wildcard patterns
        print("Detected wildcard pattern")
        # If launch_dir is provided, temporarily change to it for wildcard expansion
        original_dir = os.getcwd() if launch_dir else None
        if launch_dir:
            os.chdir(launch_dir)

        vcf_files = glob.glob(input_param)

        # Restore original directory
        if original_dir:
            os.chdir(original_dir)

        if not vcf_files:
            sys.exit(f"ERROR: No files found matching pattern: {input_param}")

        for vcf_file in sorted(vcf_files):
            if is_vcf_file(vcf_file):
                sample_id = Path(vcf_file).stem.replace('.vcf', '').replace('.gz', '')
                processed_samples.append({
                    'sample_id': sample_id,
                    'vcf_path': os.path.abspath(vcf_file)
                })
    
    elif ',' in input_param:
        # Handle comma-separated file list
        print("Detected comma-separated file list")
        file_list = [f.strip() for f in input_param.split(',')]
        
        for vcf_file in file_list:
            if not os.path.exists(vcf_file):
                sys.exit(f"ERROR: File not found: {vcf_file}")
            
            if is_vcf_file(vcf_file):
                sample_id = Path(vcf_file).stem.replace('.vcf', '').replace('.gz', '')
                processed_samples.append({
                    'sample_id': sample_id,
                    'vcf_path': os.path.abspath(vcf_file)
                })
            else:
                print(f"WARNING: Skipping non-VCF file: {vcf_file}")
    
    elif is_csv_file(input_param):
        # Handle CSV file input
        print("Detected CSV file input")
        if not os.path.exists(input_param):
            sys.exit(f"ERROR: CSV file not found: {input_param}")

        # Get the CSV file's directory to resolve relative paths
        csv_dir = os.path.dirname(os.path.abspath(input_param))

        with open(input_param, 'r') as f:
            reader = csv.DictReader(f)

            # Check required columns
            required_cols = ['sample_id', 'vcf_path']
            if not all(col in reader.fieldnames for col in required_cols):
                sys.exit(f"ERROR: CSV must contain columns: {required_cols}")

            for row in reader:
                sample_id = row['sample_id'].strip()
                vcf_path = row['vcf_path'].strip()

                if not sample_id:
                    sys.exit(f"ERROR: Empty sample_id in CSV")

                # If VCF path is relative, make it absolute (assuming from project root)
                if not os.path.isabs(vcf_path):
                    # Try resolving from the project root (go up from CSV location)
                    project_root = os.path.dirname(os.path.dirname(csv_dir))
                    vcf_path_abs = os.path.join(project_root, vcf_path)
                    if os.path.exists(vcf_path_abs):
                        vcf_path = vcf_path_abs
                    # If not found, keep original and let error handling catch it

                if not os.path.exists(vcf_path):
                    sys.exit(f"ERROR: VCF file not found: {vcf_path}")

                processed_samples.append({
                    'sample_id': sample_id,
                    'vcf_path': os.path.abspath(vcf_path)
                })
    
    elif is_vcf_file(input_param):
        # Handle single VCF file
        print("Detected single VCF file")
        if not os.path.exists(input_param):
            sys.exit(f"ERROR: VCF file not found: {input_param}")
        
        sample_id = Path(input_param).stem.replace('.vcf', '').replace('.gz', '')
        processed_samples.append({
            'sample_id': sample_id,
            'vcf_path': os.path.abspath(input_param)
        })
    
    else:
        sys.exit(f"ERROR: Unrecognized input format: {input_param}")
    
    # Validate processed samples
    if not processed_samples:
        sys.exit("ERROR: No valid VCF files found in input")
    
    # Check for duplicate sample IDs
    sample_ids = [s['sample_id'] for s in processed_samples]
    duplicates = set([x for x in sample_ids if sample_ids.count(x) > 1])
    if duplicates:
        sys.exit(f"ERROR: Duplicate sample IDs found: {duplicates}")
    
    # Validate VCF files
    for sample in processed_samples:
        vcf_path = sample['vcf_path']
        
        # Check file is readable
        try:
            with open(vcf_path, 'rb') as test_file:
                test_file.read(1)
        except IOError as e:
            sys.exit(f"ERROR: Cannot read VCF file {vcf_path}: {e}")
    
    return processed_samples

def write_output_csv(samples, output_file):
    """Write processed samples to CSV"""
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['sample_id', 'vcf_path'])
        writer.writeheader()
        writer.writerows(samples)
    
    print(f"Successfully processed {len(samples)} samples:")
    for sample in samples:
        print(f"  - {sample['sample_id']}: {sample['vcf_path']}")

def main():
    parser = argparse.ArgumentParser(description='Process various input formats for VCF liftover pipeline')
    parser.add_argument('input_param', help='Input parameter (VCF file(s) or CSV)')
    parser.add_argument('-o', '--output', default='processed_samples.csv',
                       help='Output CSV file (default: processed_samples.csv)')
    parser.add_argument('--launch-dir', default=None,
                       help='Launch directory for resolving relative paths')

    args = parser.parse_args()

    # Determine launch directory for resolving relative paths and wildcards
    launch_dir = None
    if args.launch_dir:
        launch_dir = args.launch_dir
    elif 'NXF_LAUNCH_DIR' in os.environ:
        launch_dir = os.environ['NXF_LAUNCH_DIR']

    try:
        samples = process_input(args.input_param, launch_dir=launch_dir)
        write_output_csv(samples, args.output)
        print("Input processing completed successfully")
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
