#!/usr/bin/env python3

"""
Liftover Statistics Generator
=============================
Generate comprehensive statistics for VCF liftover operations
"""

import argparse
import sys
import os
import re
import json
import csv
import subprocess
from pathlib import Path
from datetime import datetime
# Optional plotting libraries
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False

def parse_crossmap_log(log_file):
    """Parse CrossMap log file for statistics"""
    stats = {
        'sample_id': '',
        'input_variants': 0,
        'output_variants': 0,
        'unmapped_variants': 0,
        'success_rate': 0.0,
        'processing_time': 0,
        'errors': [],
        'warnings': []
    }
    
    try:
        with open(log_file, 'r') as f:
            content = f.read()
        
        # Extract sample ID from filename
        stats['sample_id'] = Path(log_file).stem.replace('.crossmap', '')
        
        # Parse variant counts
        patterns = {
            'input_variants': [
                r'Total entries:\s*(\d+)',
                r'Input variants:\s*(\d+)',
                r'Processing (\d+) variants'
            ],
            'output_variants': [
                r'Successfully lifted:\s*(\d+)',
                r'Output variants:\s*(\d+)',
                r'Lifted (\d+) variants'
            ],
            'unmapped_variants': [
                r'Failed to lift:\s*(\d+)',
                r'Unmapped variants:\s*(\d+)',
                r'Failed (\d+) variants'
            ]
        }
        
        for stat_name, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    stats[stat_name] = int(match.group(1))
                    break
        
        # Calculate success rate
        if stats['input_variants'] > 0:
            stats['success_rate'] = (stats['output_variants'] / stats['input_variants']) * 100
        
        # Extract processing time if available
        time_patterns = [
            r'Processing time:\s*(\d+\.?\d*)\s*seconds',
            r'Elapsed time:\s*(\d+\.?\d*)\s*s',
            r'Time:\s*(\d+\.?\d*)'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                stats['processing_time'] = float(match.group(1))
                break
        
        # Extract errors and warnings
        error_patterns = [
            r'ERROR:.*',
            r'Error:.*',
            r'FATAL:.*'
        ]
        
        warning_patterns = [
            r'WARNING:.*',
            r'Warning:.*',
            r'WARN:.*'
        ]
        
        for pattern in error_patterns:
            errors = re.findall(pattern, content, re.IGNORECASE)
            stats['errors'].extend(errors)
        
        for pattern in warning_patterns:
            warnings = re.findall(pattern, content, re.IGNORECASE)
            stats['warnings'].extend(warnings)
        
    except Exception as e:
        stats['errors'].append(f"Error parsing log file: {e}")
    
    return stats

def get_vcf_stats(vcf_file):
    """Get statistics from VCF file using bcftools"""
    stats = {}
    
    try:
        # Count variants
        cmd = f"bcftools view -H {vcf_file} | wc -l"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            stats['variant_count'] = int(result.stdout.strip())
        
        # Count samples
        cmd = f"bcftools query -l {vcf_file} | wc -l"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            stats['sample_count'] = int(result.stdout.strip())
        
        # Get chromosomes
        cmd = f"bcftools view -H {vcf_file} | cut -f1 | sort | uniq -c"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            chr_counts = {}
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        count = int(parts[0])
                        chrom = parts[1]
                        chr_counts[chrom] = count
            stats['chromosome_counts'] = chr_counts
        
        # Get file size
        stats['file_size_bytes'] = os.path.getsize(vcf_file)
        stats['file_size_mb'] = round(stats['file_size_bytes'] / (1024 * 1024), 2)
        
    except Exception as e:
        print(f"Warning: Could not get VCF stats for {vcf_file}: {e}")
    
    return stats

def generate_summary_report(all_stats, output_dir):
    """Generate comprehensive summary report"""
    
    # Calculate overall statistics
    total_samples = len(all_stats)
    total_input = sum(s['input_variants'] for s in all_stats)
    total_output = sum(s['output_variants'] for s in all_stats)
    total_unmapped = sum(s['unmapped_variants'] for s in all_stats)
    avg_success_rate = sum(s['success_rate'] for s in all_stats) / total_samples if total_samples > 0 else 0
    
    # Generate HTML report
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>vcf-liftover Summary Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
            .summary {{ background-color: #e8f4fd; padding: 15px; margin: 20px 0; border-radius: 5px; }}
            .metric {{ display: inline-block; margin: 10px 20px; text-align: center; }}
            .metric-value {{ font-size: 24px; font-weight: bold; color: #2c3e50; }}
            .metric-label {{ font-size: 14px; color: #7f8c8d; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .success {{ color: green; font-weight: bold; }}
            .warning {{ color: orange; font-weight: bold; }}
            .error {{ color: red; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>vcf-liftover Summary Report</h1>
            <p><strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
        
        <div class="summary">
            <h2>Overall Summary</h2>
            <div class="metric">
                <div class="metric-value">{total_samples}</div>
                <div class="metric-label">Total Samples</div>
            </div>
            <div class="metric">
                <div class="metric-value">{total_input:,}</div>
                <div class="metric-label">Input Variants</div>
            </div>
            <div class="metric">
                <div class="metric-value">{total_output:,}</div>
                <div class="metric-label">Output Variants</div>
            </div>
            <div class="metric">
                <div class="metric-value">{avg_success_rate:.1f}%</div>
                <div class="metric-label">Average Success Rate</div>
            </div>
        </div>
        
        <h2>Sample Details</h2>
        <table>
            <thead>
                <tr>
                    <th>Sample ID</th>
                    <th>Input Variants</th>
                    <th>Output Variants</th>
                    <th>Unmapped</th>
                    <th>Success Rate</th>
                    <th>File Size (MB)</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for stats in all_stats:
        status_class = "success" if stats['success_rate'] > 90 else "warning" if stats['success_rate'] > 70 else "error"
        status_text = "Good" if stats['success_rate'] > 90 else "Warning" if stats['success_rate'] > 70 else "Poor"
        
        html_content += f"""
                <tr>
                    <td>{stats['sample_id']}</td>
                    <td>{stats['input_variants']:,}</td>
                    <td>{stats['output_variants']:,}</td>
                    <td>{stats['unmapped_variants']:,}</td>
                    <td class="{status_class}">{stats['success_rate']:.1f}%</td>
                    <td>{stats.get('file_size_mb', 'N/A')}</td>
                    <td class="{status_class}">{status_text}</td>
                </tr>
        """
    
    html_content += """
            </tbody>
        </table>
    </body>
    </html>
    """
    
    # Write HTML report
    html_file = os.path.join(output_dir, 'liftover_summary.html')
    with open(html_file, 'w') as f:
        f.write(html_content)
    
    return html_file

def generate_plots(all_stats, output_dir):
    """Generate visualization plots"""

    if not PLOTTING_AVAILABLE:
        print("Warning: matplotlib/seaborn not available, skipping plots")
        return None

    try:
        
        # Set style
        plt.style.use('seaborn-v0_8')
        
        # Success rate distribution
        success_rates = [s['success_rate'] for s in all_stats]
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # Success rate histogram
        axes[0, 0].hist(success_rates, bins=20, alpha=0.7, color='skyblue')
        axes[0, 0].set_title('Success Rate Distribution')
        axes[0, 0].set_xlabel('Success Rate (%)')
        axes[0, 0].set_ylabel('Number of Samples')
        
        # Variant count comparison
        input_counts = [s['input_variants'] for s in all_stats]
        output_counts = [s['output_variants'] for s in all_stats]
        
        axes[0, 1].scatter(input_counts, output_counts, alpha=0.6)
        axes[0, 1].plot([0, max(input_counts)], [0, max(input_counts)], 'r--', alpha=0.5)
        axes[0, 1].set_title('Input vs Output Variants')
        axes[0, 1].set_xlabel('Input Variants')
        axes[0, 1].set_ylabel('Output Variants')
        
        # Success rate by sample
        sample_ids = [s['sample_id'] for s in all_stats]
        axes[1, 0].bar(range(len(sample_ids)), success_rates, color='lightgreen')
        axes[1, 0].set_title('Success Rate by Sample')
        axes[1, 0].set_xlabel('Sample Index')
        axes[1, 0].set_ylabel('Success Rate (%)')
        
        # File size distribution
        file_sizes = [s.get('file_size_mb', 0) for s in all_stats if s.get('file_size_mb', 0) > 0]
        if file_sizes:
            axes[1, 1].hist(file_sizes, bins=15, alpha=0.7, color='orange')
            axes[1, 1].set_title('Output File Size Distribution')
            axes[1, 1].set_xlabel('File Size (MB)')
            axes[1, 1].set_ylabel('Number of Files')
        
        plt.tight_layout()
        plot_file = os.path.join(output_dir, 'liftover_plots.png')
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        return plot_file

    except Exception as e:
        print(f"Warning: Error generating plots: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Generate liftover statistics')
    parser.add_argument('--log-dir', required=True, help='Directory containing CrossMap log files')
    parser.add_argument('--vcf-dir', help='Directory containing output VCF files')
    parser.add_argument('--output-dir', default='./stats', help='Output directory for reports')
    parser.add_argument('--format', choices=['html', 'json', 'csv', 'all'], default='all', help='Output format')
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    print(f"Processing log files from: {args.log_dir}")
    
    # Find all CrossMap log files
    log_files = []
    for file in os.listdir(args.log_dir):
        if file.endswith('.crossmap.log'):
            log_files.append(os.path.join(args.log_dir, file))
    
    if not log_files:
        print("No CrossMap log files found!")
        sys.exit(1)
    
    print(f"Found {len(log_files)} log files")
    
    # Parse all log files
    all_stats = []
    for log_file in log_files:
        print(f"Processing: {log_file}")
        stats = parse_crossmap_log(log_file)
        
        # Add VCF statistics if VCF directory provided
        if args.vcf_dir:
            sample_id = stats['sample_id']
            vcf_pattern = f"{sample_id}*.vcf.gz"
            
            import glob
            vcf_files = glob.glob(os.path.join(args.vcf_dir, vcf_pattern))
            if vcf_files:
                vcf_stats = get_vcf_stats(vcf_files[0])
                stats.update(vcf_stats)
        
        all_stats.append(stats)
    
    print(f"Processed {len(all_stats)} samples")
    
    # Generate reports
    if args.format in ['html', 'all']:
        html_file = generate_summary_report(all_stats, args.output_dir)
        print(f"HTML report generated: {html_file}")
    
    if args.format in ['json', 'all']:
        json_file = os.path.join(args.output_dir, 'liftover_stats.json')
        with open(json_file, 'w') as f:
            json.dump(all_stats, f, indent=2)
        print(f"JSON report generated: {json_file}")
    
    if args.format in ['csv', 'all']:
        csv_file = os.path.join(args.output_dir, 'liftover_stats.csv')
        with open(csv_file, 'w', newline='') as f:
            if all_stats:
                writer = csv.DictWriter(f, fieldnames=all_stats[0].keys())
                writer.writeheader()
                writer.writerows(all_stats)
        print(f"CSV report generated: {csv_file}")
    
    # Generate plots
    plot_file = generate_plots(all_stats, args.output_dir)
    if plot_file:
        print(f"Plots generated: {plot_file}")
    
    # Print summary
    if all_stats:
        total_input = sum(s['input_variants'] for s in all_stats)
        total_output = sum(s['output_variants'] for s in all_stats)
        avg_success = sum(s['success_rate'] for s in all_stats) / len(all_stats)
        
        print("\nSummary:")
        print(f"  Total samples: {len(all_stats)}")
        print(f"  Total input variants: {total_input:,}")
        print(f"  Total output variants: {total_output:,}")
        print(f"  Average success rate: {avg_success:.2f}%")

if __name__ == "__main__":
    main()
