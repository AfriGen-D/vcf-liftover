#!/usr/bin/env python3
"""
Generate a comprehensive HTML report for vcf-liftover pipeline (Picard pathway).

Produces a single-page HTML with tabbed interface containing:
- Summary: overall liftover statistics
- Per-Sample: detailed per-sample breakdown
- Rejection Analysis: why variants were rejected
- Pipeline Config: nextflow.config and run parameters
- Workflow: pipeline version, tools, data paths
"""

import argparse
import html
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path


def parse_picard_log(log_path):
    """Parse a Picard liftover log file."""
    sample_id = Path(log_path).name.replace('.picard.log', '')
    data = {
        'sample_id': sample_id,
        'lifted': 0,
        'rejected': 0,
        'swapped': 0,
        'elapsed': '',
        'picard_version': '',
        'java_version': '',
        'gatk_cmd': '',
    }

    try:
        text = Path(log_path).read_text()
    except OSError:
        return data

    for pattern, key in [
        (r'Lifted variants:\s*(\d+)', 'lifted'),
        (r'Rejected variants:\s*(\d+)', 'rejected'),
        (r'REF/ALT swapped variants:\s*(\d+)', 'swapped'),
    ]:
        m = re.search(pattern, text)
        if m:
            data[key] = int(m.group(1))

    m = re.search(r'Elapsed time:\s*([\d.]+)\s*minutes', text)
    if m:
        data['elapsed'] = f"{float(m.group(1)):.1f} min"

    m = re.search(r'Picard version:\s*Version:([\S]+)', text)
    if m:
        data['picard_version'] = m.group(1)

    m = re.search(r'OpenJDK.*?(\d+\.\d+\.\d+)', text)
    if m:
        data['java_version'] = m.group(1)

    # Extract the GATK command line
    m = re.search(r'(LiftoverVcf\s+--INPUT.+?)(?:\n|$)', text)
    if m:
        data['gatk_cmd'] = m.group(1).strip()

    return data


def parse_rejected_summary(summary_path):
    """Parse a rejected variant summary file."""
    sample_id = Path(summary_path).name.replace('.rejected_summary.txt', '')
    data = {
        'sample_id': sample_id,
        'total': 0,
        'snps': 0,
        'indels': 0,
        'reasons': {},
    }

    try:
        text = Path(summary_path).read_text()
    except OSError:
        return data

    for pattern, key in [
        (r'Total rejected variants:\s*(\d+)', 'total'),
        (r'SNPs:\s*(\d+)', 'snps'),
        (r'Indels:\s*(\d+)', 'indels'),
    ]:
        m = re.search(pattern, text)
        if m:
            data[key] = int(m.group(1))

    in_reasons = False
    for line in text.splitlines():
        if 'Rejection reasons:' in line:
            in_reasons = True
            continue
        if in_reasons and line.strip():
            m = re.match(r'\s*(\d+)\s+(\S+)', line)
            if m:
                data['reasons'][m.group(2)] = int(m.group(1))
            elif '===' in line:
                break

    return data


def fmt(n):
    """Format number with comma separators."""
    return f"{n:,}"


def pct(part, total):
    """Calculate percentage."""
    return f"{part / total * 100:.2f}" if total > 0 else "0.00"


def esc(s):
    """HTML-escape a string."""
    return html.escape(str(s))


def build_html(samples, rejections, config_text, args):
    """Build the complete HTML report."""
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    n_samples = len(samples)
    total_lifted = sum(s['lifted'] for s in samples)
    total_rejected = sum(s['rejected'] for s in samples)
    total_swapped = sum(s['swapped'] for s in samples)
    total_input = total_lifted + total_rejected
    success_rate = pct(total_lifted, total_input)

    # Aggregate rejection reasons
    agg_reasons = defaultdict(int)
    for r in rejections:
        for reason, count in r['reasons'].items():
            agg_reasons[reason] += count

    # Per-sample rows
    sample_rows = ""
    for s in sorted(samples, key=lambda x: x['sample_id']):
        total = s['lifted'] + s['rejected']
        rate = pct(s['lifted'], total)
        rate_class = 'success' if float(rate) >= 99 else ('warning' if float(rate) >= 95 else 'error')
        sample_rows += f"""
            <tr>
                <td>{esc(s['sample_id'])}</td>
                <td class="num">{fmt(s['lifted'] + s['rejected'])}</td>
                <td class="num">{fmt(s['lifted'])}</td>
                <td class="num">{fmt(s['rejected'])}</td>
                <td class="num">{fmt(s['swapped'])}</td>
                <td class="num {rate_class}">{rate}%</td>
                <td>{esc(s['elapsed'])}</td>
            </tr>"""

    # Rejection reason rows
    reason_rows = ""
    total_reason_count = sum(agg_reasons.values())
    for reason, count in sorted(agg_reasons.items(), key=lambda x: -x[1]):
        reason_pct = pct(count, total_reason_count)
        reason_rows += f"""
            <tr>
                <td>{esc(reason)}</td>
                <td class="num">{fmt(count)}</td>
                <td class="num">{reason_pct}%</td>
                <td><div class="bar" style="width: {pct(count, total_reason_count)}%"></div></td>
            </tr>"""

    # Per-sample rejection detail rows
    rej_detail_rows = ""
    for r in sorted(rejections, key=lambda x: x['sample_id']):
        top_reason = max(r['reasons'], key=r['reasons'].get) if r['reasons'] else 'N/A'
        top_count = r['reasons'].get(top_reason, 0)
        rej_detail_rows += f"""
            <tr>
                <td>{esc(r['sample_id'])}</td>
                <td class="num">{fmt(r['total'])}</td>
                <td class="num">{fmt(r['snps'])}</td>
                <td class="num">{fmt(r['indels'])}</td>
                <td>{esc(top_reason)} ({fmt(top_count)})</td>
            </tr>"""

    # Picard log details
    log_details = ""
    for s in sorted(samples, key=lambda x: x['sample_id']):
        log_details += f"""
        <div class="log-entry">
            <h4>{esc(s['sample_id'])}</h4>
            <table class="params-table">
                <tr><td>GATK/Picard Version</td><td>{esc(s['picard_version'] or 'N/A')}</td></tr>
                <tr><td>Java Version</td><td>{esc(s['java_version'] or 'N/A')}</td></tr>
                <tr><td>Elapsed Time</td><td>{esc(s['elapsed'] or 'N/A')}</td></tr>
                <tr><td>Lifted Variants</td><td>{fmt(s['lifted'])}</td></tr>
                <tr><td>Rejected Variants</td><td>{fmt(s['rejected'])}</td></tr>
                <tr><td>REF/ALT Swapped</td><td>{fmt(s['swapped'])}</td></tr>
            </table>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>VCF Liftover Report - {esc(args.source_build)} to {esc(args.target_build)}</title>
<style>
:root {{
    --primary: #2C3E50;
    --primary-light: #34495E;
    --success: #27AE60;
    --warning: #F39C12;
    --error: #E74C3C;
    --info: #3498DB;
    --bg: #F8F9FA;
    --card: #FFFFFF;
    --border: #DEE2E6;
    --text: #212529;
    --text-muted: #6C757D;
    --sidebar-w: 240px;
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: var(--bg); color: var(--text); line-height: 1.5; }}

/* Sidebar */
.sidebar {{ position: fixed; top: 0; left: 0; width: var(--sidebar-w); height: 100vh; background: var(--primary); color: white; display: flex; flex-direction: column; z-index: 10; }}
.sidebar-header {{ padding: 24px 20px 16px; border-bottom: 1px solid var(--primary-light); }}
.sidebar-header h1 {{ font-size: 18px; font-weight: 600; }}
.sidebar-header .subtitle {{ opacity: 0.7; font-size: 12px; margin-top: 4px; }}
.sidebar-nav {{ flex: 1; padding: 12px 0; overflow-y: auto; }}
.nav-item {{ display: block; width: 100%; padding: 10px 20px; border: none; background: none; color: rgba(255,255,255,0.7); font-size: 14px; text-align: left; cursor: pointer; transition: all 0.15s; font-family: inherit; }}
.nav-item:hover {{ background: var(--primary-light); color: white; }}
.nav-item.active {{ background: var(--primary-light); color: white; border-left: 3px solid var(--info); padding-left: 17px; font-weight: 500; }}
.sidebar-footer {{ padding: 16px 20px; border-top: 1px solid var(--primary-light); font-size: 11px; opacity: 0.5; }}

/* Main content */
.main {{ margin-left: var(--sidebar-w); min-height: 100vh; }}
.top-bar {{ background: var(--card); border-bottom: 1px solid var(--border); padding: 16px 32px; display: flex; gap: 24px; font-size: 13px; color: var(--text-muted); }}

.container {{ max-width: 1100px; padding: 24px 32px; }}

/* Metric cards */
.metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-bottom: 28px; }}
.metric {{ background: var(--card); border-radius: 8px; padding: 20px; border: 1px solid var(--border); text-align: center; }}
.metric .value {{ font-size: 32px; font-weight: 700; }}
.metric .label {{ font-size: 13px; color: var(--text-muted); margin-top: 4px; }}
.metric.success .value {{ color: var(--success); }}
.metric.error .value {{ color: var(--error); }}
.metric.warning .value {{ color: var(--warning); }}
.metric.info .value {{ color: var(--info); }}

/* Page sections (one per nav item) */
.page {{ display: none; }}
.page.active {{ display: block; }}

/* Tables */
table {{ width: 100%; border-collapse: collapse; background: var(--card); border-radius: 8px; overflow: hidden; border: 1px solid var(--border); }}
th {{ background: var(--primary); color: white; padding: 12px 16px; text-align: left; font-weight: 500; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; }}
td {{ padding: 10px 16px; border-bottom: 1px solid var(--border); font-size: 14px; }}
tr:last-child td {{ border-bottom: none; }}
tr:hover {{ background: rgba(0,0,0,0.02); }}
td.num {{ text-align: right; font-variant-numeric: tabular-nums; font-family: 'SF Mono', 'Fira Code', monospace; }}
td.success {{ color: var(--success); font-weight: 600; }}
td.warning {{ color: var(--warning); font-weight: 600; }}
td.error {{ color: var(--error); font-weight: 600; }}

/* Bar chart */
.bar {{ height: 18px; background: var(--info); border-radius: 3px; min-width: 2px; }}

/* Config */
.config-block {{ background: #1E1E1E; color: #D4D4D4; padding: 20px; border-radius: 8px; overflow-x: auto; font-family: 'SF Mono', 'Fira Code', monospace; font-size: 13px; line-height: 1.6; white-space: pre-wrap; word-wrap: break-word; max-height: 600px; overflow-y: auto; }}

/* Params table */
.params-table {{ max-width: 700px; }}
.params-table td:first-child {{ font-weight: 500; width: 220px; color: var(--text-muted); }}

/* Log entry */
.log-entry {{ margin-bottom: 16px; padding: 16px; background: var(--card); border: 1px solid var(--border); border-radius: 8px; }}
.log-entry h4 {{ margin-bottom: 8px; color: var(--primary); }}

/* Section */
.section {{ margin-bottom: 32px; }}
.section h3 {{ font-size: 18px; margin-bottom: 16px; color: var(--primary); }}

/* Footer */
.footer {{ text-align: center; padding: 24px; color: var(--text-muted); font-size: 13px; border-top: 1px solid var(--border); margin-top: 40px; }}
</style>
</head>
<body>

<!-- Sidebar Navigation -->
<div class="sidebar">
    <div class="sidebar-header">
        <h1>VCF Liftover</h1>
        <div class="subtitle">{esc(args.source_build)} &rarr; {esc(args.target_build)}</div>
    </div>
    <nav class="sidebar-nav">
        <button class="nav-item active" onclick="showPage('summary')">Summary</button>
        <button class="nav-item" onclick="showPage('samples')">Per-Sample Results</button>
        <button class="nav-item" onclick="showPage('rejections')">Rejection Analysis</button>
        <button class="nav-item" onclick="showPage('workflow')">Workflow Details</button>
        <button class="nav-item" onclick="showPage('config')">Pipeline Config</button>
        <button class="nav-item" onclick="showPage('logs')">Picard Logs</button>
        <button class="nav-item" onclick="showPage('nf-reports')">Nextflow Reports</button>
    </nav>
    <div class="sidebar-footer">v{esc(args.pipeline_version)}</div>
</div>

<!-- Main Content -->
<div class="main">
    <div class="top-bar">
        <span>Pipeline v{esc(args.pipeline_version)}</span>
        <span>Generated: {esc(now)}</span>
        <span>Samples: {n_samples}</span>
        <span>Tool: {esc(args.liftover_tool)}</span>
    </div>

    <div class="container">

    <!-- Summary Metrics (always visible) -->
    <div class="metrics">
        <div class="metric info">
            <div class="value">{fmt(total_input)}</div>
            <div class="label">Input Variants</div>
        </div>
        <div class="metric success">
            <div class="value">{fmt(total_lifted)}</div>
            <div class="label">Successfully Lifted</div>
        </div>
        <div class="metric error">
            <div class="value">{fmt(total_rejected)}</div>
            <div class="label">Rejected</div>
        </div>
        <div class="metric warning">
            <div class="value">{fmt(total_swapped)}</div>
            <div class="label">REF/ALT Swapped</div>
        </div>
        <div class="metric success">
            <div class="value">{success_rate}%</div>
            <div class="label">Success Rate</div>
        </div>
    </div>

    <!-- Page: Summary -->
    <div id="page-summary" class="page active">
        <div class="section">
            <h3>Run Parameters</h3>
            <table class="params-table">
                <tr><td>Liftover Tool</td><td>{esc(args.liftover_tool)}</td></tr>
                <tr><td>Source Build</td><td>{esc(args.source_build)}</td></tr>
                <tr><td>Target Build</td><td>{esc(args.target_build)}</td></tr>
                <tr><td>Chain File</td><td><code>{esc(args.chain_file)}</code></td></tr>
                <tr><td>Target Reference</td><td><code>{esc(args.target_fasta)}</code></td></tr>
                <tr><td>Output Directory</td><td><code>{esc(args.outdir)}</code></td></tr>
                <tr><td>Total Samples</td><td>{n_samples}</td></tr>
                <tr><td>Pipeline Version</td><td>v{esc(args.pipeline_version)}</td></tr>
            </table>
        </div>

        <div class="section">
            <h3>Liftover Results</h3>
            <table>
                <tr><th>Metric</th><th>Value</th><th>Notes</th></tr>
                <tr><td>Total Input Variants</td><td class="num">{fmt(total_input)}</td><td>Lifted + Rejected</td></tr>
                <tr><td>Successfully Lifted</td><td class="num success">{fmt(total_lifted)}</td><td>{success_rate}% success rate</td></tr>
                <tr><td>Rejected</td><td class="num error">{fmt(total_rejected)}</td><td>Could not be mapped to target build</td></tr>
                <tr><td>REF/ALT Swapped</td><td class="num warning">{fmt(total_swapped)}</td><td>Reference allele changed between builds; genotypes flipped</td></tr>
            </table>
        </div>
    </div>

    <!-- Page: Per-Sample Results -->
    <div id="page-samples" class="page">
        <div class="section">
            <h3>Per-Sample Liftover Results</h3>
            <table>
                <tr>
                    <th>Sample</th>
                    <th>Input</th>
                    <th>Lifted</th>
                    <th>Rejected</th>
                    <th>Swapped</th>
                    <th>Success</th>
                    <th>Runtime</th>
                </tr>
                {sample_rows}
            </table>
        </div>
    </div>

    <!-- Page: Rejection Analysis -->
    <div id="page-rejections" class="page">
        <div class="section">
            <h3>Rejection Reasons (All Samples)</h3>
            <table>
                <tr>
                    <th>Reason</th>
                    <th>Count</th>
                    <th>%</th>
                    <th>Distribution</th>
                </tr>
                {reason_rows}
                <tr style="font-weight:600; background:#f0f0f0;">
                    <td>Total</td>
                    <td class="num">{fmt(total_reason_count)}</td>
                    <td class="num">100%</td>
                    <td></td>
                </tr>
            </table>
        </div>

        <div class="section">
            <h3>Per-Sample Rejection Breakdown</h3>
            <table>
                <tr>
                    <th>Sample</th>
                    <th>Total Rejected</th>
                    <th>SNPs</th>
                    <th>Indels</th>
                    <th>Top Reason</th>
                </tr>
                {rej_detail_rows}
            </table>
        </div>
    </div>

    <!-- Page: Workflow Details -->
    <div id="page-workflow" class="page">
        <div class="section">
            <h3>Workflow Information</h3>
            <table class="params-table">
                <tr><td>Pipeline</td><td>vcf-liftover v{esc(args.pipeline_version)}</td></tr>
                <tr><td>Liftover Engine</td><td>GATK/Picard LiftoverVcf</td></tr>
                <tr><td>Key Flags</td><td><code>--RECOVER_SWAPPED_REF_ALT true --WRITE_ORIGINAL_POSITION true --WRITE_ORIGINAL_ALLELES true</code></td></tr>
                <tr><td>Source Build</td><td>{esc(args.source_build)}</td></tr>
                <tr><td>Target Build</td><td>{esc(args.target_build)}</td></tr>
                <tr><td>Chain File</td><td><code>{esc(Path(args.chain_file).name)}</code></td></tr>
                <tr><td>Target Reference</td><td><code>{esc(Path(args.target_fasta).name)}</code></td></tr>
            </table>
        </div>

        <div class="section">
            <h3>Pipeline Steps (Picard Pathway)</h3>
            <table>
                <tr><th>#</th><th>Process</th><th>Description</th></tr>
                <tr><td>1</td><td>INPUT_HANDLER</td><td>Parse input VCF paths or CSV</td></tr>
                <tr><td>2</td><td>INPUT_CHECK</td><td>Validate VCF format and integrity</td></tr>
                <tr><td>3</td><td>RENAME_CHROMOSOMES</td><td>Add chr prefix (required before Picard)</td></tr>
                <tr><td>4</td><td>PICARD_LIFTOVER</td><td>Coordinate liftover with REF/ALT swap recovery</td></tr>
                <tr><td>5</td><td>FILTER_REJECTED</td><td>Analyze rejected variants and reasons</td></tr>
                <tr><td>6</td><td>SORT_VCF</td><td>Sort lifted VCF by coordinate</td></tr>
                <tr><td>7</td><td>FIX_CONTIG_HEADER</td><td>Fix contig headers to match target reference</td></tr>
                <tr><td>8</td><td>INDEX_VCF</td><td>Create tabix index for final VCF</td></tr>
                <tr><td>9</td><td>LIFTOVER_STATS</td><td>Generate summary statistics</td></tr>
                <tr><td>10</td><td>GENERATE_REPORT</td><td>Generate this HTML report</td></tr>
            </table>
        </div>

        <div class="section">
            <h3>Why Picard over CrossMap?</h3>
            <table>
                <tr><th>Feature</th><th>CrossMap</th><th>Picard LiftoverVcf</th></tr>
                <tr><td>REF/ALT swap handling</td><td class="error">Sets ALT="." (variant lost)</td><td class="success">Swaps REF/ALT, flips genotypes</td></tr>
                <tr><td>Original coordinates</td><td>Not preserved</td><td class="success">Stored in INFO field</td></tr>
                <tr><td>Rejected variants</td><td>Separate .unmap file</td><td class="success">Separate VCF with FILTER reasons</td></tr>
                <tr><td>Variants affected (chr7)</td><td class="error">1,995 lost</td><td class="success">1,995 correctly swapped</td></tr>
            </table>
        </div>
    </div>

    <!-- Page: Pipeline Config -->
    <div id="page-config" class="page">
        <div class="section">
            <h3>nextflow.config</h3>
            <div class="config-block">{esc(config_text)}</div>
        </div>
    </div>

    <!-- Page: Picard Logs -->
    <div id="page-logs" class="page">
        <div class="section">
            <h3>Per-Sample Picard Log Details</h3>
            {log_details}
        </div>
    </div>

    <!-- Page: Nextflow Reports -->
    <div id="page-nf-reports" class="page">
        <div class="section">
            <h3>Nextflow Execution Reports</h3>
            <p style="color: var(--text-muted); margin-bottom: 16px; font-size: 14px;">
                These reports are generated by Nextflow at pipeline completion.
                If they appear blank, open them directly from
                <code>{esc(args.outdir)}/pipeline_info/</code>.
            </p>
            <div style="display: flex; gap: 12px; margin-bottom: 24px;">
                <a href="../pipeline_info/execution_timeline.html" target="_blank"
                   style="padding: 8px 16px; background: var(--info); color: white; border-radius: 6px; text-decoration: none; font-size: 13px;">
                   Open Timeline</a>
                <a href="../pipeline_info/execution_report.html" target="_blank"
                   style="padding: 8px 16px; background: var(--info); color: white; border-radius: 6px; text-decoration: none; font-size: 13px;">
                   Open Execution Report</a>
                <a href="../pipeline_info/execution_trace.txt" target="_blank"
                   style="padding: 8px 16px; background: var(--info); color: white; border-radius: 6px; text-decoration: none; font-size: 13px;">
                   Open Trace</a>
            </div>
        </div>

        <div class="section">
            <h3>Execution Timeline</h3>
            <iframe src="../pipeline_info/execution_timeline.html"
                    style="width:100%; height:500px; border:1px solid var(--border); border-radius:8px; background:white;"></iframe>
        </div>

        <div class="section">
            <h3>Execution Report</h3>
            <iframe src="../pipeline_info/execution_report.html"
                    style="width:100%; height:600px; border:1px solid var(--border); border-radius:8px; background:white;"></iframe>
        </div>

        <div class="section">
            <h3>Execution Trace</h3>
            <iframe src="../pipeline_info/execution_trace.txt"
                    style="width:100%; height:400px; border:1px solid var(--border); border-radius:8px; background:white; font-family:monospace;"></iframe>
        </div>
    </div>

    </div>

    <div class="footer">
        Generated by <strong>vcf-liftover</strong> v{esc(args.pipeline_version)} &mdash; {esc(now)}
    </div>
</div>

<script>
function showPage(name) {{
    document.querySelectorAll('.page').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    document.getElementById('page-' + name).classList.add('active');
    event.target.classList.add('active');
}}
</script>
</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(
        description='Generate HTML report for vcf-liftover pipeline'
    )
    parser.add_argument('--picard-logs', nargs='*', default=[])
    parser.add_argument('--rejected-summaries', nargs='*', default=[])
    parser.add_argument('--nextflow-config', default='')
    parser.add_argument('--source-build', default='hg19')
    parser.add_argument('--target-build', default='hg38')
    parser.add_argument('--liftover-tool', default='picard')
    parser.add_argument('--pipeline-version', default='2.0.0')
    parser.add_argument('--outdir', default='./results')
    parser.add_argument('--chain-file', default='')
    parser.add_argument('--target-fasta', default='')
    parser.add_argument('--output', default='liftover_report.html')

    args = parser.parse_args()

    samples = [parse_picard_log(f) for f in args.picard_logs]
    rejections = [parse_rejected_summary(f) for f in args.rejected_summaries]

    config_text = ''
    if args.nextflow_config and Path(args.nextflow_config).exists():
        config_text = Path(args.nextflow_config).read_text()

    if not samples:
        print("WARNING: No Picard log files provided.", file=sys.stderr)

    report = build_html(samples, rejections, config_text, args)
    Path(args.output).write_text(report)
    print(f"HTML report written to: {args.output}")


if __name__ == '__main__':
    main()
