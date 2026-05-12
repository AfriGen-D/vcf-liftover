#!/usr/bin/env python3
"""
Liftover Statistics Generation Script

Generates comprehensive statistics and reports for the liftover process including:
- HTML summary report with interactive tables
- Text statistics file
- CSV summary file
"""

import os
import re
import csv
import json
import subprocess
import argparse
from datetime import datetime
from pathlib import Path


def parse_crossmap_log(log_file):
    """Parse a per-sample liftover log for statistics.

    Recognises BOTH log formats:

    - **CrossMap** (legacy v1.0.0 path): `Total entries: N`, `Failed to map: N`.
      The function name preserves the original API; the file extension
      stripped here is `.crossmap`.
    - **Picard** (default since v2.0.0): the `COUNT_LIFTED_VARIANTS`
      module appends `Lifted variants: N`, `Rejected variants: N`, and
      `REF/ALT swapped variants: N` to the picard log via bcftools.
      Without parsing these, every Picard-pathway run wrote zeros to
      `liftover_statistics.txt` (the 2026-05-12 vcf-liftover regression --
      QC card showed `Total Samples: 0` etc. on Jacqui's job 68f20bcf
      that actually lifted 542,806 variants).

    Picard's lifted/rejected/swapped count tuple is the source of truth
    when present; we synthesise `input_variants` = `lifted + rejected`
    (the count BEFORE liftover that the picard log actually saw, with
    swaps already counted in `lifted`).
    """
    stats = {
        'sample_id': '',
        'input_variants': 0,
        'output_variants': 0,
        'unmapped_variants': 0,
        'success_rate': 0.0,
        'errors': []
    }

    try:
        with open(log_file, 'r') as f:
            content = f.read()

        # Extract sample ID from filename. Handles `.crossmap.log` (CrossMap
        # pathway) and `.picard.log` (Picard pathway, v2.0.0+).
        stats['sample_id'] = (
            Path(log_file).stem.replace('.crossmap', '').replace('.picard', '')
        )

        # Picard pathway: the COUNT_LIFTED_VARIANTS module emits three
        # explicit count lines at the end of the picard log.
        lifted_match = re.search(r'Lifted variants:\s*(\d+)', content)
        rejected_match = re.search(r'Rejected variants:\s*(\d+)', content)
        swapped_match = re.search(r'REF/ALT swapped variants:\s*(\d+)', content)
        if lifted_match or rejected_match:
            lifted = int(lifted_match.group(1)) if lifted_match else 0
            rejected = int(rejected_match.group(1)) if rejected_match else 0
            stats['output_variants'] = lifted
            stats['unmapped_variants'] = rejected
            stats['input_variants'] = lifted + rejected
            if swapped_match:
                stats['ref_alt_swapped'] = int(swapped_match.group(1))
        else:
            # CrossMap pathway: legacy format. "Total entries:" then
            # "Failed to map: N".
            input_match = re.search(r'Total entries:\s*(\d+)', content)
            if input_match:
                stats['input_variants'] = int(input_match.group(1))

            failed_match = re.search(r'Failed to map:\s*(\d+)', content)
            if failed_match:
                stats['unmapped_variants'] = int(failed_match.group(1))

            if stats['input_variants'] > 0 and stats['unmapped_variants'] >= 0:
                stats['output_variants'] = stats['input_variants'] - stats['unmapped_variants']

        # Calculate success rate (works for both pathways now that
        # input_variants + output_variants are populated).
        if stats['input_variants'] > 0:
            stats['success_rate'] = (stats['output_variants'] / stats['input_variants']) * 100

        # Look for errors
        error_patterns = [
            r'ERROR:.*',
            r'WARNING:.*',
            r'Failed.*'
        ]

        for pattern in error_patterns:
            errors = re.findall(pattern, content, re.IGNORECASE)
            stats['errors'].extend(errors)

    except Exception as e:
        stats['errors'].append(f"Error parsing log file: {e}")

    return stats


def count_vcf_variants(vcf_file):
    """Count variants in VCF file using bcftools"""
    try:
        cmd = f"bcftools view -H {vcf_file} | wc -l"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return int(result.stdout.strip())
    except:
        pass
    return 0


def get_file_size(file_path):
    """Get file size in MB"""
    try:
        size_bytes = os.path.getsize(file_path)
        return round(size_bytes / (1024 * 1024), 2)
    except:
        return 0


def generate_html_report(all_stats, summary_stats, params):
    """Generate HTML report"""

    html_template = '''
<!DOCTYPE html>
<html>
<head>
    <title>vcf-liftover Summary Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .summary {{ background-color: #e8f4fd; padding: 15px; margin: 20px 0; border-radius: 5px; }}
        .stats-table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        .stats-table th, .stats-table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        .stats-table th {{ background-color: #f2f2f2; }}
        .success {{ color: green; font-weight: bold; }}
        .warning {{ color: orange; font-weight: bold; }}
        .error {{ color: red; font-weight: bold; }}
        .metric {{ display: inline-block; margin: 10px 20px; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #2c3e50; }}
        .metric-label {{ font-size: 14px; color: #7f8c8d; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>vcf-liftover Summary Report</h1>
        <p><strong>Generated:</strong> {timestamp}</p>
        <p><strong>Source Build:</strong> {source_build}</p>
        <p><strong>Target Build:</strong> {target_build}</p>
    </div>

    <div class="summary">
        <h2>Overall Summary</h2>
        <div class="metric">
            <div class="metric-value">{total_samples}</div>
            <div class="metric-label">Total Samples</div>
        </div>
        <div class="metric">
            <div class="metric-value">{total_input_variants:,}</div>
            <div class="metric-label">Input Variants</div>
        </div>
        <div class="metric">
            <div class="metric-value">{total_output_variants:,}</div>
            <div class="metric-label">Output Variants</div>
        </div>
        <div class="metric">
            <div class="metric-value">{avg_success_rate:.1f}%</div>
            <div class="metric-label">Average Success Rate</div>
        </div>
    </div>

    <h2>Sample Details</h2>
    <table class="stats-table">
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
            {sample_rows}
        </tbody>
    </table>

    <h2>Pipeline Parameters</h2>
    <table class="stats-table">
        <tr><td><strong>Source Build</strong></td><td>{source_build}</td></tr>
        <tr><td><strong>Target Build</strong></td><td>{target_build}</td></tr>
        <tr><td><strong>Chain File</strong></td><td>{chain_file}</td></tr>
        <tr><td><strong>Target FASTA</strong></td><td>{target_fasta}</td></tr>
        <tr><td><strong>Chromosome Mapping</strong></td><td>{chr_mapping}</td></tr>
        <tr><td><strong>Output Directory</strong></td><td>{outdir}</td></tr>
    </table>

</body>
</html>
    '''

    # Generate sample rows
    sample_rows = ""
    for stats in all_stats:
        status_class = "success" if stats['success_rate'] > 90 else "warning" if stats['success_rate'] > 70 else "error"
        status_text = "Good" if stats['success_rate'] > 90 else "Warning" if stats['success_rate'] > 70 else "Poor"

        sample_rows += f'''
            <tr>
                <td>{stats['sample_id']}</td>
                <td>{stats['input_variants']:,}</td>
                <td>{stats['output_variants']:,}</td>
                <td>{stats['unmapped_variants']:,}</td>
                <td class="{status_class}">{stats['success_rate']:.1f}%</td>
                <td>{stats.get('file_size_mb', 'N/A')}</td>
                <td class="{status_class}">{status_text}</td>
            </tr>
        '''

    # Fill template
    html_content = html_template.format(
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        source_build=params['source_build'],
        target_build=params['target_build'],
        total_samples=summary_stats['total_samples'],
        total_input_variants=summary_stats['total_input_variants'],
        total_output_variants=summary_stats['total_output_variants'],
        avg_success_rate=summary_stats['avg_success_rate'],
        sample_rows=sample_rows,
        chain_file=params['chain_file'],
        target_fasta=params['target_fasta'],
        chr_mapping=params.get('chr_mapping', 'None'),
        outdir=params['outdir']
    )

    with open('liftover_summary_report.html', 'w') as f:
        f.write(html_content)


def generate_text_stats(all_stats, summary_stats, params):
    """Generate text statistics file"""
    with open('liftover_statistics.txt', 'w') as f:
        f.write("vcf-liftover Statistics\n")
        f.write("=" * 50 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Source Build: {params['source_build']}\n")
        f.write(f"Target Build: {params['target_build']}\n\n")

        f.write("Summary Statistics:\n")
        f.write(f"  Total Samples: {summary_stats['total_samples']}\n")
        f.write(f"  Total Input Variants: {summary_stats['total_input_variants']:,}\n")
        f.write(f"  Total Output Variants: {summary_stats['total_output_variants']:,}\n")
        f.write(f"  Total Unmapped Variants: {summary_stats['total_unmapped_variants']:,}\n")
        f.write(f"  Average Success Rate: {summary_stats['avg_success_rate']:.2f}%\n\n")

        f.write("Per-Sample Statistics:\n")
        for stats in all_stats:
            f.write(f"  {stats['sample_id']}:\n")
            f.write(f"    Input Variants: {stats['input_variants']:,}\n")
            f.write(f"    Output Variants: {stats['output_variants']:,}\n")
            f.write(f"    Success Rate: {stats['success_rate']:.2f}%\n")
            if stats['errors']:
                f.write(f"    Errors: {len(stats['errors'])}\n")
            f.write("\n")


def generate_csv_summary(all_stats):
    """Generate CSV summary file"""
    with open('sample_summary.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['sample_id', 'input_variants', 'output_variants', 'unmapped_variants',
                        'success_rate', 'file_size_mb', 'errors'])

        for stats in all_stats:
            writer.writerow([
                stats['sample_id'],
                stats['input_variants'],
                stats['output_variants'],
                stats['unmapped_variants'],
                f"{stats['success_rate']:.2f}",
                stats.get('file_size_mb', ''),
                len(stats['errors'])
            ])


def main():
    parser = argparse.ArgumentParser(
        description='Generate liftover statistics and reports'
    )
    parser.add_argument('--source-build', required=True, help='Source genome build')
    parser.add_argument('--target-build', required=True, help='Target genome build')
    parser.add_argument('--chain-file', required=True, help='Chain file used')
    parser.add_argument('--target-fasta', required=True, help='Target FASTA file used')
    parser.add_argument('--chr-mapping', default='', help='Chromosome mapping used')
    parser.add_argument('--outdir', required=True, help='Output directory')

    args = parser.parse_args()

    params = {
        'source_build': args.source_build,
        'target_build': args.target_build,
        'chain_file': args.chain_file,
        'target_fasta': args.target_fasta,
        'chr_mapping': args.chr_mapping,
        'outdir': args.outdir
    }

    print("Generating liftover statistics...")

    # Parse all CrossMap logs
    all_stats = []
    log_files = [f for f in os.listdir('.') if f.endswith('.crossmap.log')]

    for log_file in log_files:
        print(f"Processing log file: {log_file}")
        stats = parse_crossmap_log(log_file)

        # Try to get final VCF file size
        sample_id = stats['sample_id']
        vcf_pattern = f"{sample_id}.{params['target_build']}.vcf.gz"
        vcf_files = [f for f in os.listdir('.') if f == vcf_pattern]

        if vcf_files:
            vcf_file = vcf_files[0]
            stats['file_size_mb'] = get_file_size(vcf_file)
            # Double-check variant count from final VCF
            final_count = count_vcf_variants(vcf_file)
            if final_count > 0:
                stats['output_variants'] = final_count
                if stats['input_variants'] > 0:
                    stats['success_rate'] = (stats['output_variants'] / stats['input_variants']) * 100

        all_stats.append(stats)

    # Calculate summary statistics
    summary_stats = {
        'total_samples': len(all_stats),
        'total_input_variants': sum(s['input_variants'] for s in all_stats),
        'total_output_variants': sum(s['output_variants'] for s in all_stats),
        'total_unmapped_variants': sum(s['unmapped_variants'] for s in all_stats),
        'avg_success_rate': sum(s['success_rate'] for s in all_stats) / len(all_stats) if all_stats else 0
    }

    # Generate all reports
    generate_html_report(all_stats, summary_stats, params)
    generate_text_stats(all_stats, summary_stats, params)
    generate_csv_summary(all_stats)

    print(f"Statistics generated for {len(all_stats)} samples")
    print(f"Overall success rate: {summary_stats['avg_success_rate']:.2f}%")


if __name__ == "__main__":
    main()
