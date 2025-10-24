# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0] - 2025-10-24

### Added - Validation Enhancements
- **Visual Error Formatting**: ASCII box formatting for all validation messages (impossible to miss)
- **Genome Build Detection**: Automatic detection of hg19, hg38, mm9, mm10 from VCF headers
- **Build Compatibility Checking**: Critical feature preventing incorrect liftover from wrong genome builds
- **Gzip Integrity Testing**: Detects corrupted compressed files before processing
- **File Size Validation**: Detects empty and truncated files early
- **Enhanced Format Validation**: Detailed VCF format checking with specific error messages
- **Data Presence Checking**: Detects VCFs with headers but no variant records
- **Graceful Failure Handling**: Failed samples skipped, valid samples continue processing

### Added - New Validation Scripts
- `bin/format_error_message.py`: Centralized error formatting utility (275 lines)
- `bin/detect_genome_build.py`: Automatic genome build detection (425 lines)
- `bin/check_build_compatibility.py`: Build mismatch prevention (320 lines)
- `modules/check_build_mismatch.nf`: Workflow integration for build checking

### Added - Edge Case Test Infrastructure
- Created 9 edge case VCF files testing all validation features
- Added 10 test configuration CSV files for systematic testing
- Comprehensive test script with 13 total tests (4 functional + 9 validation)
- Complete documentation: README, TESTING_GUIDE, TEST_STATUS in test_data/edge_cases/

### Enhanced
- `bin/check_input.py`: Added 5 new validation checks (+300 lines)
- `bin/validate_chromosomes.py`: Visual error formatting (+50 lines)
- `workflows/liftover.nf`: Integrated Step 0 build compatibility check (+75 lines)
- `nextflow.config`: Added build compatibility parameter and Singularity path configuration
- `conf/singularity.config`: Streamlined to use only mamana namespace containers

### Changed
- Workflow now performs build compatibility check before liftover (optional, enabled by default)
- Sample-level validation status files enable filtering of failed samples
- Increased Singularity pull timeout from 20 to 60 minutes

### Documentation
- Updated README.md highlighting new validation features
- Enhanced docs/guide/troubleshooting.md with container configuration solutions
- Added dev_docs/VALIDATION_IMPLEMENTATION_REPORT.md (comprehensive technical report)
- Added dev_docs/validation_enhancements.md (implementation details)
- Updated docs/guide/input-files.md with validation information

### Fixed
- Visual error messages now consistently formatted across all validation scripts
- Chromosome validation distinguishes naming differences (OK) from missing chromosomes (ERROR)

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
