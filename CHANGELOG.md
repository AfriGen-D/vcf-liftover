# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- AfriGen-D branding and logo to README
- Comprehensive support links (helpdesk, discussions, website)
- CHANGELOG.md for version tracking
- CITATIONS.md for tool references
- CODE_OF_CONDUCT.md for community guidelines
- GitHub issue templates for bug reports and feature requests
- Issue template configuration with helpdesk links

### Changed
- Updated README with AfriGen-D template structure
- Enhanced documentation links and support resources
- Improved pipeline summary and introduction sections

## [1.0.0] - 2025-01-XX

### Added
- Initial release of VCF Liftover pipeline
- Input validation for VCF files
- Chromosome validation and compatibility checking
- CrossMap-based coordinate liftover
- Automatic chromosome naming detection and correction
- VCF sorting and compression
- Quality control statistics and reports
- Comprehensive HTML report generation
- Multi-file batch processing support
- Test data and profiles
- VitePress documentation site
- GitHub Actions CI/CD workflows
- Docker and Singularity container support
- SLURM HPC cluster configuration

### Features
- Support for hg19 to hg38 conversions
- Automatic chromosome name mapping (chr1 vs 1)
- Parallel processing of multiple VCF files
- Detailed statistics tracking
- Success rate monitoring
- Failed variant reporting

## Version History

For older versions and detailed commit history, see the [GitHub Releases](https://github.com/AfriGen-D/vcf-liftover/releases) page.
