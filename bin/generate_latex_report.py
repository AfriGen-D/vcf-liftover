#!/usr/bin/env python3
"""
Generate a LaTeX PDF report for vcf-liftover pipeline (Picard pathway).

Parses Picard liftover logs and rejected variant summaries to produce
a professional PDF report with summary statistics, per-sample breakdown,
and rejection analysis.

Usage:
    generate_latex_report.py \
        --picard-logs sample1.picard.log sample2.picard.log \
        --rejected-summaries sample1.rejected_summary.txt ... \
        --source-build hg19 --target-build hg38 \
        --liftover-tool picard --pipeline-version 2.0.0 \
        --output liftover_report.tex
"""

import argparse
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path


def escape_latex(s):
    """Escape special LaTeX characters."""
    replacements = [
        ('\\', r'\textbackslash{}'),
        ('&', r'\&'), ('%', r'\%'), ('$', r'\$'),
        ('#', r'\#'), ('_', r'\_'), ('{', r'\{'),
        ('}', r'\}'), ('~', r'\textasciitilde{}'),
        ('^', r'\textasciicircum{}'),
    ]
    for old, new in replacements:
        s = s.replace(old, new)
    return s


def parse_picard_log(log_path):
    """Parse a Picard liftover log file.

    Extracts variant counts from the echo lines written by picard_liftover.nf:
        Lifted variants: N
        Rejected variants: N
        REF/ALT swapped variants: N
    """
    sample_id = Path(log_path).name.replace('.picard.log', '')
    data = {
        'sample_id': sample_id,
        'lifted': 0,
        'rejected': 0,
        'swapped': 0,
        'elapsed': '',
        'warnings': [],
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

    data['warnings'] = [
        line.strip() for line in text.splitlines()
        if 'WARN' in line or 'WARNING' in line
    ]

    return data


def parse_rejected_summary(summary_path):
    """Parse a rejected variant summary file.

    Expected format from filter_rejected.nf:
        === Rejected Variants Summary: sample_id ===
        Total rejected variants: N
        SNPs: N
        Indels: N

        Rejection reasons:
            960 NoTarget
             17 IndelStraddlesMultipleIntervals
    """
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

    # Parse rejection reasons: lines like "    960 NoTarget"
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


def format_number(n):
    """Format number with comma separators."""
    return f"{n:,}"


def build_tex(samples, rejections, args):
    """Build the LaTeX document string."""
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    n_samples = len(samples)
    total_lifted = sum(s['lifted'] for s in samples)
    total_rejected = sum(s['rejected'] for s in samples)
    total_swapped = sum(s['swapped'] for s in samples)
    total_input = total_lifted + total_rejected
    success_rate = (total_lifted / total_input * 100) if total_input > 0 else 0

    # Aggregate rejection reasons across all samples
    agg_reasons = defaultdict(int)
    for r in rejections:
        for reason, count in r['reasons'].items():
            agg_reasons[reason] += count

    tex = r"""\documentclass[11pt,a4paper]{article}
\usepackage[margin=2.5cm]{geometry}
\usepackage{longtable}
\usepackage{booktabs}
\usepackage[table]{xcolor}
\usepackage{hyperref}
\usepackage{fancyhdr}
\usepackage{lastpage}

\hypersetup{
    colorlinks=true,
    linkcolor=blue!60!black,
    urlcolor=blue!60!black,
    pdftitle={VCF Liftover Report},
    pdfauthor={vcf-liftover pipeline}
}

\definecolor{headerblue}{HTML}{2C3E50}
\definecolor{successgreen}{HTML}{27AE60}
\definecolor{warningamber}{HTML}{F39C12}
\definecolor{errorred}{HTML}{E74C3C}
\definecolor{lightgray}{HTML}{F5F5F5}

\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small\textcolor{headerblue}{vcf-liftover """ + escape_latex(args.pipeline_version) + r"""}}
\fancyhead[R]{\small\textcolor{headerblue}{""" + escape_latex(now) + r"""}}
\fancyfoot[C]{\small Page \thepage\ of \pageref{LastPage}}

\begin{document}

% ── Title ──────────────────────────────────────────────────────────
\begin{center}
{\LARGE\bfseries\textcolor{headerblue}{VCF Liftover Report}}\\[0.5em]
{\large """ + escape_latex(args.source_build) + r""" $\rightarrow$ """ + escape_latex(args.target_build) + r"""}\\[0.3em]
{\small Generated: """ + escape_latex(now) + r""" \quad|\quad Pipeline v""" + escape_latex(args.pipeline_version) + r"""}
\end{center}
\vspace{1em}
\hrule
\vspace{1.5em}

% ── Run Parameters ─────────────────────────────────────────────────
\section*{Run Parameters}
\begin{tabular}{@{}ll@{}}
\toprule
\textbf{Parameter} & \textbf{Value} \\
\midrule
Liftover tool & """ + escape_latex(args.liftover_tool) + r""" \\
Source build & """ + escape_latex(args.source_build) + r""" \\
Target build & """ + escape_latex(args.target_build) + r""" \\
Total samples & """ + str(n_samples) + r""" \\
\bottomrule
\end{tabular}
\vspace{1.5em}

% ── Summary Metrics ────────────────────────────────────────────────
\section*{Summary}

\begin{center}
\setlength{\fboxsep}{12pt}
\colorbox{lightgray}{%
\begin{tabular}{cccc}
\textbf{Input Variants} & \textbf{Lifted} & \textbf{Rejected} & \textbf{REF/ALT Swapped} \\[0.3em]
{\Large\bfseries """ + format_number(total_input) + r"""} &
{\Large\bfseries\textcolor{successgreen}{""" + format_number(total_lifted) + r"""}} &
{\Large\bfseries\textcolor{errorred}{""" + format_number(total_rejected) + r"""}} &
{\Large\bfseries\textcolor{warningamber}{""" + format_number(total_swapped) + r"""}} \\[0.3em]
& \small """ + f"{success_rate:.2f}" + r"""\% success & &
\end{tabular}%
}
\end{center}
\vspace{1.5em}

"""

    # ── Per-sample table ───────────────────────────────────────────
    tex += r"""% ── Per-Sample Results ──────────────────────────────────────────────
\section*{Per-Sample Results}

\begin{longtable}{lrrrr}
\toprule
\textbf{Sample} & \textbf{Lifted} & \textbf{Rejected} & \textbf{Swapped} & \textbf{Success \%} \\
\midrule
\endfirsthead
\toprule
\textbf{Sample} & \textbf{Lifted} & \textbf{Rejected} & \textbf{Swapped} & \textbf{Success \%} \\
\midrule
\endhead
\bottomrule
\endfoot
"""

    for i, s in enumerate(sorted(samples, key=lambda x: x['sample_id'])):
        total = s['lifted'] + s['rejected']
        rate = (s['lifted'] / total * 100) if total > 0 else 0
        row_color = r'\rowcolor{lightgray}' if i % 2 == 0 else ''
        tex += f"{row_color} {escape_latex(s['sample_id'])} & "
        tex += f"{format_number(s['lifted'])} & "
        tex += f"{format_number(s['rejected'])} & "
        tex += f"{format_number(s['swapped'])} & "
        tex += f"{rate:.2f}\\% \\\\\n"

    tex += r"""\end{longtable}
\vspace{1em}

"""

    # ── Rejection Analysis ─────────────────────────────────────────
    if agg_reasons:
        tex += r"""% ── Rejection Analysis ──────────────────────────────────────────────
\section*{Rejection Analysis}

\begin{tabular}{@{}lr@{}}
\toprule
\textbf{Rejection Reason} & \textbf{Count} \\
\midrule
"""
        for reason, count in sorted(agg_reasons.items(), key=lambda x: -x[1]):
            tex += f"{escape_latex(reason)} & {format_number(count)} \\\\\n"

        total_rej_reasons = sum(agg_reasons.values())
        tex += r"""\midrule
\textbf{Total} & \textbf{""" + format_number(total_rej_reasons) + r"""} \\
\bottomrule
\end{tabular}
\vspace{1.5em}

"""

    # ── Per-sample rejection detail (if multiple samples) ──────────
    if len(rejections) > 1:
        tex += r"""\subsection*{Per-Sample Rejection Breakdown}

\begin{longtable}{lrrll}
\toprule
\textbf{Sample} & \textbf{Total} & \textbf{SNPs} & \textbf{Indels} & \textbf{Top Reason} \\
\midrule
\endfirsthead
\toprule
\textbf{Sample} & \textbf{Total} & \textbf{SNPs} & \textbf{Indels} & \textbf{Top Reason} \\
\midrule
\endhead
\bottomrule
\endfoot
"""
        for i, r in enumerate(sorted(rejections, key=lambda x: x['sample_id'])):
            top_reason = max(r['reasons'], key=r['reasons'].get) if r['reasons'] else 'N/A'
            row_color = r'\rowcolor{lightgray}' if i % 2 == 0 else ''
            tex += f"{row_color} {escape_latex(r['sample_id'])} & "
            tex += f"{format_number(r['total'])} & "
            tex += f"{format_number(r['snps'])} & "
            tex += f"{format_number(r['indels'])} & "
            tex += f"{escape_latex(top_reason)} \\\\\n"

        tex += r"""\end{longtable}
\vspace{1em}

"""

    # ── Footer ─────────────────────────────────────────────────────
    tex += r"""\vfill
\hrule
\vspace{0.5em}
\begin{center}
\small\textcolor{gray}{Generated by \textbf{vcf-liftover} v""" + escape_latex(args.pipeline_version) + r"""
\quad|\quad """ + escape_latex(now) + r"""}
\end{center}

\end{document}
"""

    return tex


def main():
    parser = argparse.ArgumentParser(
        description='Generate LaTeX PDF report for vcf-liftover pipeline'
    )
    parser.add_argument('--picard-logs', nargs='*', default=[],
                        help='Picard liftover log files')
    parser.add_argument('--rejected-summaries', nargs='*', default=[],
                        help='Rejected variant summary files')
    parser.add_argument('--source-build', default='hg19')
    parser.add_argument('--target-build', default='hg38')
    parser.add_argument('--liftover-tool', default='picard')
    parser.add_argument('--pipeline-version', default='2.0.0')
    parser.add_argument('--output', default='liftover_report.tex')

    args = parser.parse_args()

    # Parse all inputs
    samples = [parse_picard_log(f) for f in args.picard_logs]
    rejections = [parse_rejected_summary(f) for f in args.rejected_summaries]

    if not samples:
        print("WARNING: No Picard log files provided. Report will be empty.",
              file=sys.stderr)

    # Build and write .tex
    tex = build_tex(samples, rejections, args)
    Path(args.output).write_text(tex)
    print(f"LaTeX report written to: {args.output}")


if __name__ == '__main__':
    main()
