#!/usr/bin/env python
"""
Build Compatibility Checker

Checks if VCF genome build matches the expected build for the chain file.
Prevents incorrect liftover results from build mismatches.

Example Problem:
    VCF: hg38 (already GRCh38)
    Chain: hg19ToHg38.over.chain.gz (expects hg19 input!)
    Result: INCOMPATIBLE - will produce wrong coordinates

Usage:
    check_build_compatibility.py \\
        --vcf sample.vcf.gz \\
        --chain hg19ToHg38.over.chain.gz \\
        --target-ref GRCh38.fa.fai \\
        --output report.txt
"""

import argparse
import sys
import os
import re

# Import build detection
try:
    from detect_genome_build import detect_genome_build
    from format_error_message import format_critical_error, format_info, format_warning
except ImportError as e:
    print(f"ERROR: Cannot import required modules: {e}", file=sys.stderr)
    print("Ensure detect_genome_build.py and format_error_message.py are in the same directory", file=sys.stderr)
    sys.exit(1)


def parse_chain_filename(chain_file):
    """
    Parse chain file name to extract source and target builds.

    Examples:
        hg19ToHg38.over.chain.gz → (hg19, hg38)
        GRCh37_to_GRCh38.chain.gz → (hg19, hg38)
        mm9ToMm10.over.chain.gz → (mm9, mm10)

    Returns:
        tuple: (source_build, target_build) or (None, None)
    """
    filename = os.path.basename(chain_file).lower()

    # Pattern 1: buildTo Build (e.g., hg19ToHg38)
    pattern1 = r'(hg\d+|grch\d+|mm\d+|b\d+)to(hg\d+|grch\d+|mm\d+|b\d+)'
    match = re.search(pattern1, filename, re.IGNORECASE)
    if match:
        source = normalize_build_name(match.group(1))
        target = normalize_build_name(match.group(2))
        return source, target

    # Pattern 2: build_to_build (e.g., GRCh37_to_GRCh38)
    pattern2 = r'(hg\d+|grch\d+|mm\d+|b\d+)[_-]to[_-](hg\d+|grch\d+|mm\d+|b\d+)'
    match = re.search(pattern2, filename, re.IGNORECASE)
    if match:
        source = normalize_build_name(match.group(1))
        target = normalize_build_name(match.group(2))
        return source, target

    return None, None


def normalize_build_name(build):
    """Normalize build names to canonical form"""
    build_lower = build.lower()

    # Human genome builds
    if build_lower in ['grch37', 'b37']:
        return 'hg19'
    elif build_lower in ['grch38', 'b38']:
        return 'hg38'
    elif build_lower.startswith('hg'):
        return build_lower
    elif build_lower.startswith('mm'):
        return build_lower

    return build


def check_compatibility(vcf_file, chain_file, target_ref, sample_id="unknown"):
    """
    Check if VCF build is compatible with chain file.

    Returns:
        dict: {
            'compatible': bool,
            'vcf_build': str,
            'chain_source': str,
            'chain_target': str,
            'target_build': str,
            'issues': list,
            'warnings': list
        }
    """
    result = {
        'compatible': True,
        'vcf_build': 'unknown',
        'chain_source': 'unknown',
        'chain_target': 'unknown',
        'target_build': 'unknown',
        'issues': [],
        'warnings': []
    }

    # 1. Detect VCF build
    vcf_build, vcf_method, vcf_details = detect_genome_build(vcf_path=vcf_file, verbose=False)
    result['vcf_build'] = vcf_build if vcf_build else 'unknown'
    result['vcf_detection_method'] = vcf_method
    result['vcf_detection_details'] = vcf_details

    if not vcf_build:
        result['warnings'].append(f"Could not detect VCF build: {vcf_details}")

    # 2. Parse chain file name
    chain_source, chain_target = parse_chain_filename(chain_file)
    result['chain_source'] = chain_source if chain_source else 'unknown'
    result['chain_target'] = chain_target if chain_target else 'unknown'

    if not chain_source or not chain_target:
        result['warnings'].append(
            f"Could not parse chain file name: {os.path.basename(chain_file)}. "
            "Cannot validate source/target builds."
        )

    # 3. Detect target reference build
    target_build, target_method, target_details = detect_genome_build(reference_path=target_ref, verbose=False)
    result['target_build'] = target_build if target_build else 'unknown'
    result['target_detection_method'] = target_method
    result['target_detection_details'] = target_details

    if not target_build:
        result['warnings'].append(f"Could not detect target reference build: {target_details}")

    # 4. Compatibility checks
    issues = []

    # Check 1: VCF build should match chain source
    if vcf_build and chain_source and vcf_build != 'unknown' and chain_source != 'unknown':
        if vcf_build != chain_source:
            issues.append(
                f"VCF build ({vcf_build}) does not match chain file source ({chain_source}). "
                f"Chain file expects {chain_source} input but VCF is {vcf_build}."
            )

    # Check 2: Target reference should match chain target
    if target_build and chain_target and target_build != 'unknown' and chain_target != 'unknown':
        if target_build != chain_target:
            issues.append(
                f"Target reference build ({target_build}) does not match chain file target ({chain_target}). "
                f"Chain file converts to {chain_target} but reference is {target_build}."
            )

    # Check 3: VCF should not already be at target build (no liftover needed)
    if vcf_build and target_build and vcf_build != 'unknown' and target_build != 'unknown':
        if vcf_build == target_build:
            result['warnings'].append(
                f"VCF is already {vcf_build}, same as target reference ({target_build}). "
                "Liftover may not be necessary."
            )

    if issues:
        result['compatible'] = False
        result['issues'] = issues

    return result


def format_compatibility_report(result, sample_id, vcf_file, chain_file, target_ref):
    """Format a detailed compatibility report"""
    lines = []

    lines.append("=" * 76)
    lines.append(f"BUILD COMPATIBILITY REPORT: {sample_id}")
    lines.append("=" * 76)
    lines.append("")

    # Files
    lines.append("Input Files:")
    lines.append(f"  VCF: {vcf_file}")
    lines.append(f"  Chain: {os.path.basename(chain_file)}")
    lines.append(f"  Target Reference: {os.path.basename(target_ref)}")
    lines.append("")

    # Detected builds
    lines.append("Detected Builds:")
    lines.append(f"  VCF Build: {result['vcf_build']}")
    if result.get('vcf_detection_method'):
        lines.append(f"    Method: {result['vcf_detection_method']}")
        lines.append(f"    Details: {result['vcf_detection_details']}")

    lines.append(f"  Chain Source → Target: {result['chain_source']} → {result['chain_target']}")

    lines.append(f"  Target Reference Build: {result['target_build']}")
    if result.get('target_detection_method'):
        lines.append(f"    Method: {result['target_detection_method']}")
        lines.append(f"    Details: {result['target_detection_details']}")
    lines.append("")

    # Compatibility result
    if result['compatible']:
        lines.append("✓ COMPATIBILITY: PASSED")
        lines.append("  All builds are compatible for liftover")
    else:
        lines.append("❌ COMPATIBILITY: FAILED")
        lines.append("  Build mismatch detected - liftover will produce incorrect results")

    lines.append("")

    # Issues
    if result['issues']:
        lines.append("Issues:")
        for issue in result['issues']:
            lines.append(f"  ❌ {issue}")
        lines.append("")

    # Warnings
    if result['warnings']:
        lines.append("Warnings:")
        for warning in result['warnings']:
            lines.append(f"  ⚠️  {warning}")
        lines.append("")

    lines.append("=" * 76)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Check genome build compatibility for VCF liftover',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--vcf', required=True, help='Input VCF file')
    parser.add_argument('--chain', required=True, help='Chain file for liftover')
    parser.add_argument('--target-ref', required=True, help='Target reference genome (.fa or .fa.fai)')
    parser.add_argument('--sample-id', default='unknown', help='Sample identifier')
    parser.add_argument('-o', '--output', required=True, help='Output report file')

    args = parser.parse_args()

    # Validate input files exist
    for filepath, name in [(args.vcf, 'VCF'), (args.chain, 'Chain'), (args.target_ref, 'Target reference')]:
        # For reference, check both .fa and .fa.fai
        if name == 'Target reference':
            if not os.path.exists(filepath) and not os.path.exists(f"{filepath}.fai"):
                print(format_critical_error(
                    title=f"{name} File Not Found",
                    message_lines=[f"File: {filepath}"],
                    suggestions=["Check if file path is correct", "Ensure file exists"]
                ), file=sys.stderr)
                sys.exit(1)
        elif not os.path.exists(filepath):
            print(format_critical_error(
                title=f"{name} File Not Found",
                message_lines=[f"File: {filepath}"],
                suggestions=["Check if file path is correct", "Ensure file exists"]
            ), file=sys.stderr)
            sys.exit(1)

    # Check compatibility
    result = check_compatibility(args.vcf, args.chain, args.target_ref, args.sample_id)

    # Format report
    report = format_compatibility_report(result, args.sample_id, args.vcf, args.chain, args.target_ref)

    # Write report
    with open(args.output, 'w') as f:
        f.write(report)

    # Print to console
    print(report)

    # Create marker file if incompatible
    if not result['compatible']:
        marker_file = "BUILD_MISMATCH_DETECTED"
        with open(marker_file, 'w') as f:
            f.write(f"Sample: {args.sample_id}\n")
            f.write(f"VCF build: {result['vcf_build']}\n")
            f.write(f"Expected: {result['chain_source']}\n")
            f.write("\n".join(result['issues']))

        print(format_critical_error(
            title="Build Mismatch Detected",
            message_lines=[
                f"VCF build: {result['vcf_build']}",
                f"Chain expects: {result['chain_source']} → {result['chain_target']}",
                f"Target reference: {result['target_build']}",
                "",
                "This configuration will produce INCORRECT RESULTS!"
            ],
            suggestions=[
                f"If VCF is truly {result['vcf_build']}, use a {result['vcf_build']}To{result['chain_target']} chain file",
                f"If VCF should be {result['chain_source']}, verify the VCF build",
                "Convert VCF to correct build before liftover",
                f"Check detailed report: {args.output}"
            ]
        ), file=sys.stderr)

        # Exit with error
        sys.exit(1)
    else:
        print(format_info(
            title="Compatibility Check Passed",
            message_lines=[
                f"VCF ({result['vcf_build']}) is compatible with chain file ({result['chain_source']}→{result['chain_target']})",
                "Ready to proceed with liftover"
            ]
        ))

        # Exit success
        sys.exit(0)


if __name__ == '__main__':
    main()
