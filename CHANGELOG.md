# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Per-chromosome split toggle (`--split_by_chr`).** The flag was already declared in `nextflow.config` but no module consumed it. New `modules/split_by_chr.nf` (`vcf_processing` label) runs after `INDEX_VCF` when enabled and publishes one `<basename>.<chr>.vcf.gz` (plus `.tbi`) per chromosome present in the input under `${outdir}/per_chromosome/`. Eliminates the manual `bcftools view -r chrN` step users had to run before submitting to imputationserver2 (which rejects multi-chromosome VCFs). Exposed in `workflow.yaml` as a checkbox input and as a new `split_by_chr` stage in the progress timeline. CI's `test` profile sets `split_by_chr = true` and validates the per-chromosome outputs.
- `--fix_mismatched_ref` toggle (opt-in, default `false`) + new `--source_fasta` param. When enabled, runs `bcftools +fixref -m flip -d` against the source build's reference before liftover — flips REF/ALT for variants where alleles are merely on the opposite strand, drops the rest. New module `modules/fix_mismatched_ref.nf` under `vcf_processing` label. Wired into the Picard pathway in `workflows/liftover.nf` between the build-compat check and `GENERATE_CHR_MAPPING`.
- `FILTER_REJECTED` now emits a remediation hint to `rejected_summary.txt` when `MismatchedRefAllele` is the dominant rejection reason (≥100 absolute, ≥100 total, ≥50% of rejections), pointing at the new `--fix_mismatched_ref` toggle so users don't have to discover the workaround manually.
- `modules/prepare_vcf_for_picard.nf`: BCF→VCF.gz prep step under `vcf_processing` label, runs ahead of `PICARD_LIFTOVER` and symlinks for `.vcf.gz` inputs.
- `modules/count_lifted_variants.nf`: `bcftools`-based variant count step that appends `Lifted variants:` / `Rejected variants:` / `REF/ALT swapped variants:` to the Picard log, under `vcf_processing` label.

### Changed
- **`chain_file` and `target_fasta` are now auto-derived from `source_build` + `target_build`.** `nextflow.config` resolves them via `CHAIN_FILES` / `FASTA_FILES` lookup tables at config load when the caller leaves them null. CLI overrides (`--chain_file`, `--target_fasta`) still work, but the FedImpute `workflow.yaml` no longer exposes them as separate UI dropdowns. A 2026-05-12 production submission asked for `hg19 -> hg38` but inherited the legacy `hg38ToHg19` chain default and `hg19.fasta` target reference, producing 270k `MismatchedRefAllele` rejections and 22 MB of silently corrupt output. With four independent dropdowns there was no way to detect the inconsistency at submit time; cross-validation in `workflow.yaml` has no schema support either. Deriving the two file paths from the build pair makes the misconfiguration unrepresentable.
- **`PICARD_LIFTOVER` now calls `picard LiftoverVcf` directly** instead of `gatk LiftoverVcf`. Same algorithm (GATK4 wraps Picard for this tool) but no longer requires the ~2.3 GB `broadinstitute/gatk` image — the existing 250 MB `mamana/picard:3.3.0` is sufficient.
- `conf/k8s.config`: `vcf_processing` → `mamana/vcf-processing:latest` (was `mamana/picard:3.3.0` which has no `bcftools`).
- `conf/docker.config`: `vcf_processing` → `mamana/vcf-processing:latest`, `picard` → `mamana/picard:3.3.0` (was `broadinstitute/gatk:4.5.0.0`).
- `workflows/liftover.nf`: Picard pathway is now `RENAME_CHROMOSOMES` → `PREPARE_VCF_FOR_PICARD` → `PICARD_LIFTOVER` → `COUNT_LIFTED_VARIANTS`, so each process runs in a container that has every tool it calls.
- `nextflow.config:35`: `"${HOME}/.singularity"` → `"${System.getenv('HOME')}/.singularity"` (Nextflow 26.x rejects the older syntax).

### Fixed
- **`GENERATE_CHR_MAPPING` no longer dies with misleading "Could not extract chromosomes from VCF" on the k8s profile.** Root cause was a 2026-04-14 regression in `conf/k8s.config` that mapped `vcf_processing` to a container without `bcftools`; the `bcftools query ... 2>/dev/null | sort -u` then produced empty stdout and the script emitted a misleading user-facing error. Every k8s vcf-liftover run had been failing this way for ~4 weeks. The `2>/dev/null` is also removed so the next regression of this kind surfaces immediately.
- **`PICARD_LIFTOVER` now uses `set -o pipefail`** so picard's exit code isn't swallowed by `tee`'s in `picard ... 2>&1 | tee log`. Previously a picard exception would still leave the bash script logging "Picard LiftoverVcf completed".
- **Disabled HTSJDK Snappy native-lib compression for picard temp streams** (`-Dsamjdk.snappy.disable=true`). `mamana/picard:3.3.0` lacks `libsnappy`, so `SortingCollection.spillToDisk()` crashed once `MAX_RECORDS_IN_RAM=100000` was exceeded (which it is for any realistic input). HTSJDK falls back to GZIP, which is in the container.

## [2.0.0] - 2026-03-06

### Added - Picard LiftoverVcf Engine
- **GATK/Picard LiftoverVcf** as the default liftover tool, replacing CrossMap
- `--liftover_tool` parameter to select between `picard` (default) and `crossmap` (legacy)
- `--RECOVER_SWAPPED_REF_ALT true`: Correctly handles REF/ALT swaps when the reference allele changes between genome builds
- `--WRITE_ORIGINAL_POSITION true`: Preserves original coordinates in INFO field
- `--WRITE_ORIGINAL_ALLELES true`: Preserves original alleles in INFO field
- `modules/picard_liftover.nf`: New Picard LiftoverVcf process
- `modules/filter_rejected.nf`: Rejected variant analysis and summary
- Rejected variants output with detailed rejection reasons

### Changed
- **Default liftover tool changed from CrossMap to Picard** (breaking change)
- Workflow reordered for Picard: chromosome renaming now happens BEFORE liftover (Picard requires matching contig names)
- Container: `broadinstitute/gatk:4.5.0.0` for the `picard` label
- Memory allocation: 32GB default for Picard (loads full reference genome)
- Java heap: automatically calculated as `task.memory - 4GB`

### Fixed
- **REF/ALT swap handling**: CrossMap sets ALT="." when the reference allele changes between builds, silently losing variants. Picard correctly swaps REF/ALT and flips genotypes. On chr7 alone, 1,995 variants were affected, including pharmacogenomically critical rs776746 (CYP3A5*3).
- **Genotype consistency**: Picard flips genotypes when swapping REF/ALT (e.g., B37 1/1 becomes 0/0 when the old ALT becomes the new REF), ensuring genotype calls remain semantically correct.

### Backward Compatibility
- CrossMap is still available via `--liftover_tool crossmap`
- All existing input formats (single VCF, multiple VCFs, CSV) remain supported
- All validation features from v1.1.0 are preserved

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
