#!/usr/bin/env python
"""
Genome Build Detection Script

Detects genome build (hg19/GRCh37, hg38/GRCh38, etc.) from VCF files and reference genomes.

Detection Methods:
1. VCF header ##reference line
2. VCF ##contig lines (chromosome lengths match known builds)
3. Reference .fai file (chromosome lengths)
4. Filename patterns (hg19, hg38, GRCh37, GRCh38)

Supports:
- Human: hg19/GRCh37, hg38/GRCh38
- Mouse: mm9, mm10, mm39
- Common model organisms

Usage:
    # Detect from VCF
    detect_genome_build.py --vcf input.vcf.gz

    # Detect from reference
    detect_genome_build.py --reference genome.fa.fai

    # Both
    detect_genome_build.py --vcf input.vcf.gz --reference genome.fa.fai
"""

import argparse
import sys
import gzip
import os
from pathlib import Path

# Import error formatting
try:
    from format_error_message import format_info, format_warning
except ImportError:
    def format_info(title, msgs): return f"{title}: " + "; ".join(msgs if isinstance(msgs, list) else [msgs])
    def format_warning(title, msgs, ctx=None): return f"WARNING {title}: " + "; ".join(msgs if isinstance(msgs, list) else [msgs])


# Known chromosome lengths for different genome builds
# Format: {build: {chrom: length}}
KNOWN_BUILDS = {
    'hg19': {
        '1': 249250621, '2': 242193529, '3': 198295559, '4': 191154276,
        '5': 180915260, '6': 171115067, '7': 159138663, '8': 146364022,
        '9': 141213431, '10': 135534747, '11': 135006516, '12': 133851895,
        '13': 115169878, '14': 107349540, '15': 102531392, '16': 90354753,
        '17': 81195210, '18': 78077248, '19': 59128983, '20': 63025520,
        '21': 48129895, '22': 51304566, 'X': 155270560, 'Y': 59373566,
        'MT': 16569, 'M': 16569
    },
    'hg38': {
        '1': 248956422, '2': 242193529, '3': 198295559, '4': 190214555,
        '5': 181538259, '6': 170805979, '7': 159345973, '8': 145138636,
        '9': 138394717, '10': 133797422, '11': 135086622, '12': 133275309,
        '13': 114364328, '14': 107043718, '15': 101991189, '16': 90338345,
        '17': 83257441, '18': 80373285, '19': 58617616, '20': 64444167,
        '21': 46709983, '22': 50818468, 'X': 156040895, '55': 57227415,
        'MT': 16569, 'M': 16569
    },
    'mm10': {
        '1': 195471971, '2': 182113224, '3': 160039680, '4': 156508116,
        '5': 151834684, '6': 149736546, '7': 145441459, '8': 129401213,
        '9': 124595110, '10': 130694993, '11': 122082543, '12': 120129022,
        '13': 120421639, '14': 124902244, '15': 104043685, '16': 98207768,
        '17': 94987271, '18': 90702639, '19': 61431566, 'X': 171031299,
        'Y': 91744698, 'MT': 16299, 'M': 16299
    },
    'mm9': {
        '1': 197195432, '2': 181748087, '3': 159599783, '4': 155630120,
        '5': 152537259, '6': 149517037, '7': 152524553, '8': 131738871,
        '9': 124076172, '10': 129993255, '11': 121843856, '12': 121257530,
        '13': 120284312, '14': 125194864, '15': 103494974, '16': 98319150,
        '17': 95272651, '18': 90772031, '19': 61342430, 'X': 166650296,
        'Y': 15902555, 'MT': 16299, 'M': 16299
    }
}

# Build aliases
BUILD_ALIASES = {
    'GRCh37': 'hg19',
    'GRCh38': 'hg38',
    'b37': 'hg19',
    'b38': 'hg38',
    'hg19': 'hg19',
    'hg38': 'hg38',
    'mm9': 'mm9',
    'mm10': 'mm10'
}


def open_vcf(vcf_path):
    """Open VCF file (handles gzipped and plain)"""
    if vcf_path.endswith('.gz'):
        return gzip.open(vcf_path, 'rt')
    return open(vcf_path, 'r')


def normalize_chrom(chrom):
    """Remove chr prefix if present"""
    if chrom.startswith('chr'):
        return chrom[3:]
    return chrom


def detect_from_vcf_header(vcf_path):
    """
    Detect build from VCF ##reference header line.

    Examples:
        ##reference=file:///path/to/GRCh38.fa
        ##reference=hg19.fa
        ##reference=GRCh37_reference.fa
    """
    try:
        with open_vcf(vcf_path) as f:
            for line in f:
                if not line.startswith('##'):
                    break  # Past header

                if line.startswith('##reference='):
                    ref_value = line.split('=', 1)[1].strip()

                    # Check for build keywords in reference line
                    ref_lower = ref_value.lower()
                    for alias, canonical in BUILD_ALIASES.items():
                        if alias.lower() in ref_lower:
                            return canonical, f'VCF header ##reference={ref_value[:50]}'

        return None, 'No ##reference line found in VCF header'

    except Exception as e:
        return None, f'Error reading VCF header: {e}'


def detect_from_vcf_contigs(vcf_path):
    """
    Detect build from VCF ##contig header lines by matching chromosome lengths.

    Example:
        ##contig=<ID=chr1,length=249250621>  → hg19 (chr1 is 249250621 in hg19)
        ##contig=<ID=chr1,length=248956422>  → hg38 (chr1 is 248956422 in hg38)
    """
    try:
        contigs = {}

        with open_vcf(vcf_path) as f:
            for line in f:
                if not line.startswith('##'):
                    break

                if line.startswith('##contig='):
                    # Parse: ##contig=<ID=chr1,length=249250621>
                    if 'ID=' in line and 'length=' in line:
                        try:
                            id_part = line.split('ID=')[1].split(',')[0]
                            length_part = line.split('length=')[1].split(',')[0].split('>')[0]

                            chrom = normalize_chrom(id_part)
                            length = int(length_part)

                            contigs[chrom] = length
                        except (IndexError, ValueError):
                            continue

        if not contigs:
            return None, 'No ##contig lines with lengths found'

        # Match against known builds
        best_match = None
        best_match_count = 0

        for build, known_lengths in KNOWN_BUILDS.items():
            match_count = 0
            for chrom, length in contigs.items():
                if chrom in known_lengths and known_lengths[chrom] == length:
                    match_count += 1

            if match_count > best_match_count:
                best_match = build
                best_match_count = match_count

        if best_match and best_match_count >= 3:  # Need at least 3 matching chromosomes
            confidence = (best_match_count / len(contigs)) * 100
            return best_match, f'Matched {best_match_count}/{len(contigs)} contigs ({confidence:.0f}% confidence)'

        return None, f'Insufficient contig matches (best: {best_match_count} chromosomes)'

    except Exception as e:
        return None, f'Error parsing VCF contigs: {e}'


def detect_from_filename(filepath):
    """Detect build from filename patterns"""
    filename = os.path.basename(filepath).lower()

    for alias, canonical in BUILD_ALIASES.items():
        if alias.lower() in filename:
            return canonical, f'Filename contains "{alias}"'

    return None, 'No build keywords in filename'


def detect_from_reference_fai(fai_path):
    """
    Detect build from reference .fai file by matching chromosome lengths.

    .fai format: chrom\tlength\t...
    """
    try:
        if not os.path.exists(fai_path):
            # Try adding .fai extension
            if not fai_path.endswith('.fai') and os.path.exists(f"{fai_path}.fai"):
                fai_path = f"{fai_path}.fai"
            else:
                return None, f'File not found: {fai_path}'

        contigs = {}

        with open(fai_path, 'r') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    chrom = normalize_chrom(parts[0])
                    try:
                        length = int(parts[1])
                        contigs[chrom] = length
                    except ValueError:
                        continue

        if not contigs:
            return None, 'No valid chromosome lengths in .fai file'

        # Match against known builds
        best_match = None
        best_match_count = 0

        for build, known_lengths in KNOWN_BUILDS.items():
            match_count = 0
            for chrom, length in contigs.items():
                if chrom in known_lengths and known_lengths[chrom] == length:
                    match_count += 1

            if match_count > best_match_count:
                best_match = build
                best_match_count = match_count

        if best_match and best_match_count >= 3:
            confidence = (best_match_count / len(contigs)) * 100
            return best_match, f'Matched {best_match_count}/{len(contigs)} chromosomes ({confidence:.0f}% confidence)'

        return None, f'Insufficient chromosome matches (best: {best_match_count})'

    except Exception as e:
        return None, f'Error reading .fai file: {e}'


def detect_genome_build(vcf_path=None, reference_path=None, verbose=False):
    """
    Detect genome build from VCF and/or reference files.

    Returns:
        tuple: (build, method, details) or (None, None, error_message)
    """
    results = []

    # Try VCF detection methods
    if vcf_path:
        if not os.path.exists(vcf_path):
            return None, None, f'VCF file not found: {vcf_path}'

        # Method 1: VCF header ##reference
        build, details = detect_from_vcf_header(vcf_path)
        if build:
            results.append((build, 'VCF header', details))
        elif verbose:
            print(f"  VCF header check: {details}", file=sys.stderr)

        # Method 2: VCF ##contig lines
        build, details = detect_from_vcf_contigs(vcf_path)
        if build:
            results.append((build, 'VCF contigs', details))
        elif verbose:
            print(f"  VCF contigs check: {details}", file=sys.stderr)

        # Method 3: VCF filename
        build, details = detect_from_filename(vcf_path)
        if build:
            results.append((build, 'VCF filename', details))
        elif verbose:
            print(f"  VCF filename check: {details}", file=sys.stderr)

    # Try reference detection
    if reference_path:
        # Method 4: Reference .fai file
        build, details = detect_from_reference_fai(reference_path)
        if build:
            results.append((build, 'Reference .fai', details))
        elif verbose:
            print(f"  Reference .fai check: {details}", file=sys.stderr)

        # Method 5: Reference filename
        build, details = detect_from_filename(reference_path)
        if build:
            results.append((build, 'Reference filename', details))
        elif verbose:
            print(f"  Reference filename check: {details}", file=sys.stderr)

    # Analyze results
    if not results:
        return None, None, 'Could not detect genome build from any method'

    # Check for consensus
    builds = [r[0] for r in results]
    if len(set(builds)) == 1:
        # All methods agree
        return results[0][0], results[0][1], results[0][2]
    else:
        # Conflicting results - prefer contig-based detection over filename
        priority_order = ['VCF contigs', 'Reference .fai', 'VCF header', 'VCF filename', 'Reference filename']
        for method in priority_order:
            for build, meth, details in results:
                if meth == method:
                    warning = f"Multiple builds detected: {set(builds)}. Using {build} from {method}"
                    return build, method, f"{details} (WARNING: {warning})"

        # Fallback to first result
        return results[0][0], results[0][1], f"{results[0][2]} (WARNING: Conflicting detections)"


def main():
    parser = argparse.ArgumentParser(
        description='Detect genome build from VCF or reference files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Detect from VCF
    %(prog)s --vcf sample.vcf.gz

    # Detect from reference
    %(prog)s --reference genome.fa.fai

    # Detect and compare both
    %(prog)s --vcf sample.vcf.gz --reference genome.fa.fai

Supported builds:
    - Human: hg19/GRCh37, hg38/GRCh38
    - Mouse: mm9, mm10
        """
    )
    parser.add_argument('--vcf', help='VCF file path')
    parser.add_argument('--reference', help='Reference genome .fai file path')
    parser.add_argument('-o', '--output', help='Output file for build information')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()

    if not args.vcf and not args.reference:
        parser.error("At least one of --vcf or --reference is required")

    print(format_info(
        title="Genome Build Detection",
        message_lines=[
            f"VCF file: {args.vcf if args.vcf else 'Not provided'}",
            f"Reference: {args.reference if args.reference else 'Not provided'}"
        ]
    ))

    # Detect build
    build, method, details = detect_genome_build(
        vcf_path=args.vcf,
        reference_path=args.reference,
        verbose=args.verbose
    )

    # Prepare output
    output_lines = []

    if build:
        output_lines.append(f"Detected build: {build}")
        output_lines.append(f"Detection method: {method}")
        output_lines.append(f"Details: {details}")

        print(format_info(
            title="Build Detected",
            message_lines=[
                f"Build: {build}",
                f"Method: {method}",
                f"Details: {details}"
            ]
        ))
    else:
        output_lines.append(f"Build: unknown")
        output_lines.append(f"Reason: {details}")

        print(format_warning(
            title="Build Detection Failed",
            message_lines=[f"Reason: {details}"],
            context="Build will be marked as 'unknown'"
        ))

    # Write output file
    if args.output:
        with open(args.output, 'w') as f:
            f.write('\n'.join(output_lines))
        print(f"\nBuild information written to: {args.output}")

    # Exit with appropriate code
    sys.exit(0 if build else 1)


if __name__ == '__main__':
    main()
