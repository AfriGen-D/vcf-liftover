# Test Scenarios for vcf-liftover

## Generated Test Datasets

### 1. Small Dataset (small_chr22.vcf.gz)
- **Purpose**: Quick testing and validation
- **Variants**: 5 variants on chromosome 22
- **Samples**: 2 samples
- **Use case**: `--input test_data/small_chr22.vcf.gz`

### 2. Medium Multi-chromosome (medium_multi_chr.vcf.gz)
- **Purpose**: Test multi-chromosome processing
- **Variants**: 20 variants across chromosomes 21-22
- **Samples**: 3 samples
- **Use case**: `--input test_data/medium_multi_chr.vcf.gz`

### 3. Large Single Sample (large_single_sample.vcf.gz)
- **Purpose**: Performance testing with many variants
- **Variants**: 100 variants on chromosome 22
- **Samples**: 1 sample
- **Use case**: `--input test_data/large_single_sample.vcf.gz`

### 4. Population Dataset (population_20samples.vcf.gz)
- **Purpose**: Test with many samples
- **Variants**: 20 variants on chromosome 22
- **Samples**: 20 samples
- **Use case**: `--input test_data/population_20samples.vcf.gz`

### 5. Edge Cases (edge_cases.vcf.gz)
- **Purpose**: Test complex variants and edge positions
- **Variants**: 5 variants including indels
- **Samples**: 1 sample
- **Features**: Insertions, deletions, complex variants
- **Use case**: `--input test_data/edge_cases.vcf.gz`

### 6. Multi-allelic (multiallelic.vcf.gz)
- **Purpose**: Test multi-allelic variant handling
- **Variants**: 4 variants with overlapping positions
- **Samples**: 2 samples
- **Use case**: `--input test_data/multiallelic.vcf.gz`

## Batch Processing Tests

### CSV Input Tests
1. **Single sample**: `--input test_data/single_sample.csv`
2. **Multiple samples**: `--input test_data/multiple_samples.csv`
3. **Population study**: `--input test_data/population_study.csv`

### Wildcard Tests
1. **All VCF files**: `--input "test_data/*.vcf.gz"`
2. **Specific pattern**: `--input "test_data/small_*.vcf.gz"`

## Performance Benchmarks

| Dataset | Variants | Samples | Expected Time | Use Case |
|---------|----------|---------|---------------|----------|
| Small | 5 | 2 | <5s | Quick validation |
| Medium | 20 | 3 | <10s | Multi-chr testing |
| Large | 100 | 1 | <15s | Performance test |
| Population | 20 | 20 | <20s | Many samples |
| Edge Cases | 5 | 1 | <10s | Complex variants |

## Testing Commands

```bash
# Quick test
./nextflow run main.nf -profile test,singularity --input test_data/small_chr22.vcf.gz

# Multi-chromosome test
./nextflow run main.nf -profile test,singularity --input test_data/medium_multi_chr.vcf.gz

# Performance test
./nextflow run main.nf -profile test,singularity --input test_data/large_single_sample.vcf.gz

# Population test
./nextflow run main.nf -profile test,singularity --input test_data/population_20samples.vcf.gz

# Batch processing test
./nextflow run main.nf -profile test,singularity --input test_data/multiple_samples.csv

# Wildcard test
./nextflow run main.nf -profile test,singularity --input "test_data/small_*.vcf.gz"
```
