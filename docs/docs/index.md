# vcf-liftover Documentation ​

Comprehensive documentation for the vcf-liftover pipeline - your complete reference for understanding, configuring, and troubleshooting VCF liftover analyses.

## Overview ​

vcf-liftover is a Nextflow pipeline that converts genomic coordinates between reference genome builds (hg19 to hg38) using CrossMap. This documentation provides detailed information about every aspect of the pipeline usage.

## Documentation Sections ​

### Core Concepts ​

- [Understanding Results](/docs/understanding-results) - Complete guide to interpreting liftover output and validation reports
- [Liftover Methods](/docs/liftover-methods) - Detailed explanation of CrossMap integration and coordinate conversion
- [Single File Analysis](/docs/single-file) - In-depth single-file processing

### Processing Workflows ​

- [Multi-File Processing](/docs/multi-file) - Comprehensive multi-file analysis with CSV batch input
- [Quality Control](/docs/quality-control) - Complete QC procedures, validation workflows, and automated quality assessment

### Reference Materials ​

- [Troubleshooting](/docs/troubleshooting) - Complete problem-solving guide including validation issues

## New Features ​

### Automated Validation ​

vcf-liftover now includes built-in validation for liftover results:

- Automatic quality assessment during coordinate conversion
- Liftover success rate validation to detect conversion issues
- Coordinate accuracy verification to confirm conversions were applied correctly
- Interactive HTML reports for comprehensive result review

### Enhanced Quality Control ​

- Real-time validation during pipeline execution
- Comprehensive validation reports with actionable recommendations
- Configurable validation thresholds for different data types
- Integration with existing QC workflows

## When to Use Documentation vs Tutorials ​

### Use Documentation when you need to:

- Understand how liftover processes work internally
- Get comprehensive parameter information
- Implement quality control procedures
- Troubleshoot complex issues
- Reference detailed command options

### Use Tutorials when you want to:

- Get started quickly with vcf-liftover
- Follow step-by-step workflows
- Learn specific techniques
- Practice with guided examples

## Documentation Organization ​

Each documentation page provides:

- Comprehensive coverage of the topic
- Detailed examples with real commands
- Advanced configuration options
- Best practices and recommendations
- Troubleshooting for common issues
- Cross-references to related topics

## Getting Started with Documentation ​

If you're new to vcf-liftover documentation:

1. Start with [Understanding Results](/docs/understanding-results) - Learn how to interpret liftover output
2. Review [Liftover Methods](/docs/liftover-methods) - Understand your conversion options
3. Explore [Quality Control](/docs/quality-control) - Learn validation procedures
4. Reference [Troubleshooting](/docs/troubleshooting) - When you need to solve problems

## Documentation vs Tutorial Content ​

| Documentation | Tutorials |
|---------------|-----------|
| Comprehensive reference | Step-by-step learning |
| Detailed explanations | Focused exercises |
| All options covered | Essential steps only |
| Problem-solving focus | Achievement-oriented |
| Reference material | Learning material |

## Contributing to Documentation ​

Found an issue or want to improve the documentation?

- Visit our [GitHub repository](https://github.com/AfriGen-D/vcf-liftover)
- Submit issues or suggestions
- Contact [AfriGen-D](https://afrigen-d.org)

## Related Resources ​

- [Tutorials](/tutorials/) - Step-by-step learning exercises
- [Reference](/reference/) - Complete parameter documentation
- [Examples](/examples/) - Ready-to-use examples
- [Guide](/guide/) - Getting started information
