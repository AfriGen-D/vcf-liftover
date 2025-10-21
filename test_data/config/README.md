# Test Data for vcf-liftover

This directory contains comprehensive test datasets for validating the vcf-liftover pipeline.

## Quick Start

### Generate Test Data
```bash
python3 bin/generate_test_data.py
```

### Run Single Test with Test Reference
```bash
./nextflow run main.nf -profile test,singularity \
  --input test_data/small_chr22.vcf.gz \
  --target_fasta test_data/GRCh38_test_regions.fa
```

### Run Single Test with Full Reference
```bash
./nextflow run main.nf -profile test,singularity \
  --input test_data/small_chr22.vcf.gz \
  --target_fasta /cbio/dbs/references/GRCh38_reference_genome/GRCh38_full_analysis_set_plus_decoy_hla.fa
```

### Run Comprehensive Test Suite
```bash
./run_comprehensive_tests.sh
```

## Test Datasets

| Dataset | Variants | Samples | Purpose |
|---------|----------|---------|---------|
| `small_chr22.vcf.gz` | 5 | 2 | Quick validation |
| `medium_multi_chr.vcf.gz` | 20 | 3 | Multi-chromosome testing |
| `large_single_sample.vcf.gz` | 100 | 1 | Performance testing |
| `population_20samples.vcf.gz` | 20 | 20 | Many samples testing |
| `edge_cases.vcf.gz` | 5 | 1 | Complex variants (indels) |
| `multiallelic.vcf.gz` | 4 | 2 | Multi-allelic variants |

## CSV Batch Files

| CSV File | Description |
|----------|-------------|
| `single_sample.csv` | Single sample batch test |
| `multiple_samples.csv` | Multiple samples batch test |
| `population_study.csv` | Population study batch test |

## Test Reference FASTA Files

### Full Chromosome References
- **`GRCh38_chr21_chr22.fa`** - Complete chromosomes 21 & 22 (95 MB, 97% size reduction)
- **`GRCh38_chr21_chr22.fa.fai`** - FASTA index file

### Region-Specific References
- **`GRCh38_test_regions.fa`** - chr21:1-10M, chr22:1-20M (30 MB, 99.1% size reduction)
- **`GRCh38_test_regions.fa.fai`** - FASTA index file

### Legacy References
- **`hg38_chr22.fa.gz`** - Original chr22 reference (12 MB)

## Generate Test Reference FASTA

```bash
# Extract full chromosomes
python3 bin/generate_test_reference.py --chromosomes chr21,chr22 --output test_data/GRCh38_chr21_chr22.fa

# Extract specific regions
python3 bin/generate_test_reference.py --regions chr21:1-10000000,chr22:1-20000000 --output test_data/GRCh38_test_regions.fa
```

## Expected Results

- **Success Rate**: 80-100% for most datasets
- **Processing Time**: <30 seconds per dataset
- **Output**: Lifted VCF files with proper hg38 coordinates

## Files Description

- **VCF Files**: Compressed VCF files with realistic variant data
- **CSV Files**: Batch processing input files
- **TEST_SCENARIOS.md**: Detailed testing documentation
- **README.md**: This file

## Notes

- All test data uses hg19 coordinates for liftover to hg38
- Variants are positioned on chromosomes 21-22 for realistic testing
- Test data includes various variant types: SNPs, indels, complex variants
- Use absolute paths when running tests to avoid path resolution issues
