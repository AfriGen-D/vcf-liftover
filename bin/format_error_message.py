#!/usr/bin/env python
"""
Error Message Formatting Utility

Provides consistent, user-friendly error message formatting across the pipeline.
Inspired by the checkref pipeline's visual error presentation.

Usage:
    from format_error_message import format_critical_error, format_warning, format_info

    # Critical error (stops workflow)
    msg = format_critical_error(
        title="VCF File Not Found",
        message_lines=["File: sample.vcf.gz", "Expected location: /data/"],
        suggestions=["Check file path", "Use absolute paths"]
    )

    # Warning (continues workflow)
    msg = format_warning(
        title="Small File Detected",
        message_lines=["File size: 523 bytes"],
        context="This may be normal for test data"
    )

    # Info message
    msg = format_info(
        title="Validation Complete",
        message_lines=["5 samples validated", "All checks passed"]
    )
"""

import sys


def format_critical_error(title, message_lines, suggestions=None):
    """
    Format a critical error message with visual ASCII box borders.

    Args:
        title: Error title (will be centered and capitalized)
        message_lines: List of message lines or single string
        suggestions: List of suggestion strings (optional)

    Returns:
        Formatted error message string
    """
    width = 76
    output = []

    # Convert single string to list
    if isinstance(message_lines, str):
        message_lines = [message_lines]

    # Top border
    output.append("╔" + "═" * width + "╗")

    # Title (centered with emoji)
    title_text = f"❌  {title.upper()}  ❌"
    padding_left = (width - len(title_text)) // 2
    padding_right = width - len(title_text) - padding_left
    output.append("║" + " " * padding_left + title_text + " " * padding_right + "║")

    # Bottom border
    output.append("╚" + "═" * width + "╝")
    output.append("")

    # Message lines
    for line in message_lines:
        output.append(line)
    output.append("")

    # Suggestions section
    if suggestions:
        if isinstance(suggestions, str):
            suggestions = [suggestions]
        output.append("Suggestions:")
        for suggestion in suggestions:
            output.append(f"  • {suggestion}")
        output.append("")

    return "\n".join(output)


def format_warning(title, message_lines, context=None):
    """
    Format a warning message with visual ASCII box borders.

    Args:
        title: Warning title
        message_lines: List of message lines or single string
        context: Additional context information (optional)

    Returns:
        Formatted warning message string
    """
    width = 76
    output = []

    # Convert single string to list
    if isinstance(message_lines, str):
        message_lines = [message_lines]

    # Top border
    output.append("╔" + "═" * width + "╗")

    # Title (centered with emoji)
    title_text = f"⚠️  {title.upper()}  ⚠️"
    padding_left = (width - len(title_text)) // 2
    padding_right = width - len(title_text) - padding_left
    output.append("║" + " " * padding_left + title_text + " " * padding_right + "║")

    # Bottom border
    output.append("╚" + "═" * width + "╝")
    output.append("")

    # Message lines
    for line in message_lines:
        output.append(line)
    output.append("")

    # Context section
    if context:
        output.append("Context:")
        if isinstance(context, list):
            for ctx in context:
                output.append(f"  {ctx}")
        else:
            output.append(f"  {context}")
        output.append("")

    return "\n".join(output)


def format_info(title, message_lines):
    """
    Format an informational message with visual ASCII box borders.

    Args:
        title: Info title
        message_lines: List of message lines or single string

    Returns:
        Formatted info message string
    """
    width = 76
    output = []

    # Convert single string to list
    if isinstance(message_lines, str):
        message_lines = [message_lines]

    # Top border
    output.append("╔" + "═" * width + "╗")

    # Title (centered with emoji)
    title_text = f"ℹ️  {title.upper()}  ℹ️"
    padding_left = (width - len(title_text)) // 2
    padding_right = width - len(title_text) - padding_left
    output.append("║" + " " * padding_left + title_text + " " * padding_right + "║")

    # Bottom border
    output.append("╚" + "═" * width + "╝")
    output.append("")

    # Message lines
    for line in message_lines:
        output.append(line)
    output.append("")

    return "\n".join(output)


def format_success(title, stats=None, message_lines=None):
    """
    Format a success message with statistics.

    Args:
        title: Success title
        stats: Dictionary of statistics (optional)
        message_lines: Additional message lines (optional)

    Returns:
        Formatted success message string
    """
    width = 76
    output = []

    # Top border
    output.append("╔" + "═" * width + "╗")

    # Title (centered with emoji)
    title_text = f"✓  {title.upper()}  ✓"
    padding_left = (width - len(title_text)) // 2
    padding_right = width - len(title_text) - padding_left
    output.append("║" + " " * padding_left + title_text + " " * padding_right + "║")

    # Bottom border
    output.append("╚" + "═" * width + "╝")
    output.append("")

    # Message lines
    if message_lines:
        if isinstance(message_lines, str):
            message_lines = [message_lines]
        for line in message_lines:
            output.append(line)
        output.append("")

    # Statistics section
    if stats:
        output.append("Statistics:")
        for key, value in stats.items():
            # Format key nicely (replace underscores with spaces, title case)
            formatted_key = key.replace('_', ' ').title()
            output.append(f"  • {formatted_key}: {value}")
        output.append("")

    return "\n".join(output)


def format_section_header(title, char="─"):
    """
    Format a section header with horizontal line.

    Args:
        title: Section title
        char: Character to use for line (default: ─)

    Returns:
        Formatted section header
    """
    width = 76
    line = char * width
    return f"\n{title}\n{line}\n"


def format_validation_report(sample_id, checks, overall_status):
    """
    Format a comprehensive validation report.

    Args:
        sample_id: Sample identifier
        checks: List of (check_name, status, details) tuples
        overall_status: 'PASSED' or 'FAILED'

    Returns:
        Formatted validation report string
    """
    output = []
    width = 76

    # Header
    output.append("═" * width)
    output.append(f"VALIDATION REPORT: {sample_id}")
    output.append("═" * width)
    output.append("")

    # Individual checks
    for check_name, status, details in checks:
        if status == 'PASSED':
            status_symbol = "✓"
        elif status == 'FAILED':
            status_symbol = "❌"
        elif status == 'WARNING':
            status_symbol = "⚠️"
        else:
            status_symbol = "ℹ️"

        output.append(f"{status_symbol} {check_name}: {status}")
        if details:
            for detail in details:
                output.append(f"  {detail}")
        output.append("")

    # Overall result
    output.append("─" * width)
    if overall_status == 'PASSED':
        output.append(f"✓ OVERALL RESULT: {overall_status}")
    else:
        output.append(f"❌ OVERALL RESULT: {overall_status}")
    output.append("═" * width)

    return "\n".join(output)


# Example usage and testing
if __name__ == "__main__":
    print("Testing error message formatting...\n")

    # Test critical error
    print(format_critical_error(
        title="VCF File Not Found",
        message_lines=[
            "Sample: sample1",
            "Expected path: /data/sample1.vcf.gz",
            "Current directory: /users/mamana/vcf-liftover"
        ],
        suggestions=[
            "Check if the file path is correct",
            "Verify the file exists: ls -la /data/sample1.vcf.gz",
            "Use absolute paths instead of relative paths"
        ]
    ))

    # Test warning
    print(format_warning(
        title="Small File Detected",
        message_lines=[
            "File: test.vcf.gz",
            "Size: 523 bytes"
        ],
        context="This may be normal for test data, but could indicate truncation"
    ))

    # Test info
    print(format_info(
        title="Validation Complete",
        message_lines=[
            "5 samples validated",
            "All checks passed",
            "Ready to proceed with liftover"
        ]
    ))

    # Test success
    print(format_success(
        title="Pipeline Completed",
        stats={
            'total_samples': 5,
            'variants_lifted': '1,234,567',
            'average_success_rate': '98.5%',
            'total_runtime': '2h 15m'
        },
        message_lines=["All samples processed successfully"]
    ))

    # Test validation report
    print(format_validation_report(
        sample_id="sample1",
        checks=[
            ("File Existence", "PASSED", ["File found at expected location"]),
            ("Gzip Integrity", "PASSED", ["Gzip compression valid"]),
            ("VCF Format", "PASSED", ["Valid VCF header and structure"]),
            ("Data Presence", "WARNING", ["Only 10 variants found", "Expected more for production data"]),
            ("Chromosome Names", "PASSED", ["All chromosomes present in reference"])
        ],
        overall_status="PASSED"
    ))
