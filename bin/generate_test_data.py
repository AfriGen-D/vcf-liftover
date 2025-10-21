#!/usr/bin/env python3
"""
Generate comprehensive test data for vcf-liftover pipeline
Creates realistic VCF files with various use cases and scenarios
"""

import os
import gzip
import random
from datetime import datetime

def create_vcf_header(sample_names, reference="hg19", contig_info=None):
    """Create VCF header with proper format"""
    header = [
        "##fileformat=VCFv4.2",
        "##fileDate=" + datetime.now().strftime("%Y%m%d"),
        "##source=vcf-liftover-test-data-generator",
        "##reference=" + reference,
        "##INFO=<ID=AC,Number=A,Type=Integer,Description=\"Allele count in genotypes\">",
        "##INFO=<ID=AF,Number=A,Type=Float,Description=\"Allele Frequency\">",
        "##INFO=<ID=AN,Number=1,Type=Integer,Description=\"Total number of alleles in called genotypes\">",
        "##INFO=<ID=DP,Number=1,Type=Integer,Description=\"Approximate read depth\">",
        "##FORMAT=<ID=GT,Number=1,Type=String,Description=\"Genotype\">",
        "##FORMAT=<ID=DP,Number=1,Type=Integer,Description=\"Approximate read depth\">",
        "##FORMAT=<ID=GQ,Number=1,Type=Integer,Description=\"Genotype Quality\">",
    ]
    
    # Add contig information
    if contig_info:
        for contig, length in contig_info.items():
            header.append(f"##contig=<ID={contig},length={length}>")
    
    # Add column header
    columns = ["#CHROM", "POS", "ID", "REF", "ALT", "QUAL", "FILTER", "INFO", "FORMAT"] + sample_names
    header.append("\t".join(columns))
    
    return header

def generate_variant(chrom, pos, ref, alt, sample_names, af=0.5, dp=30):
    """Generate a single variant line"""
    variant_id = f"rs{random.randint(1000000, 9999999)}"
    qual = random.randint(20, 60)
    
    # Calculate allele counts
    an = len(sample_names) * 2
    ac = max(1, int(an * af))
    
    info = f"AC={ac};AF={af:.3f};AN={an};DP={dp}"
    format_field = "GT:DP:GQ"
    
    # Generate genotypes
    genotypes = []
    for _ in sample_names:
        if random.random() < af:
            gt = random.choice(["0/1", "1/1"])
        else:
            gt = "0/0"
        
        sample_dp = random.randint(15, 50)
        gq = random.randint(20, 60)
        genotypes.append(f"{gt}:{sample_dp}:{gq}")
    
    variant_line = [
        str(chrom), str(pos), variant_id, ref, alt, str(qual), "PASS",
        info, format_field
    ] + genotypes
    
    return "\t".join(variant_line)

def create_test_vcf(filename, variants_data, sample_names, reference="hg19", compress=True):
    """Create a VCF file with specified variants"""
    
    # Determine contigs from variants
    contigs = {}
    for chrom, pos, _, _ in variants_data:
        if chrom not in contigs:
            contigs[chrom] = 250000000  # Default chromosome length
    
    header = create_vcf_header(sample_names, reference, contigs)
    
    # Generate variants
    variants = []
    for chrom, pos, ref, alt in variants_data:
        af = random.uniform(0.1, 0.9)
        variant = generate_variant(chrom, pos, ref, alt, sample_names, af)
        variants.append(variant)
    
    # Write file
    if compress:
        with gzip.open(filename, 'wt') as f:
            for line in header:
                f.write(line + "\n")
            for variant in variants:
                f.write(variant + "\n")
    else:
        with open(filename, 'w') as f:
            for line in header:
                f.write(line + "\n")
            for variant in variants:
                f.write(variant + "\n")

def main():
    """Generate comprehensive test datasets"""

    print("Generating comprehensive test data for vcf-liftover...")

    # Ensure test_data directory exists
    import os
    os.makedirs("dev_docs/test_data", exist_ok=True)

    # Test Case 1: Small dataset with known coordinates (chr22)
    print("1. Creating small test dataset (chr22)...")
    small_variants = [
        ("22", 16050000, "G", "A"),
        ("22", 16100000, "C", "T"),
        ("22", 16150000, "A", "G"),
        ("22", 16200000, "T", "C"),
        ("22", 16250000, "G", "T"),
    ]
    create_test_vcf("dev_docs/test_data/small_chr22.vcf.gz", small_variants, ["SAMPLE1", "SAMPLE2"])
    
    # Test Case 2: Medium dataset with multiple chromosomes
    print("2. Creating medium multi-chromosome dataset...")
    medium_variants = []
    for chrom in ["21", "22"]:
        for i in range(10):
            pos = 16000000 + (i * 50000)
            ref = random.choice(["A", "C", "G", "T"])
            alt = random.choice([x for x in ["A", "C", "G", "T"] if x != ref])
            medium_variants.append((chrom, pos, ref, alt))
    
    create_test_vcf("dev_docs/test_data/medium_multi_chr.vcf.gz", medium_variants,
                   ["SAMPLE1", "SAMPLE2", "SAMPLE3"])
    
    # Test Case 3: Large single sample dataset
    print("3. Creating large single sample dataset...")
    large_variants = []
    for i in range(100):
        pos = 16000000 + (i * 10000)
        ref = random.choice(["A", "C", "G", "T"])
        alt = random.choice([x for x in ["A", "C", "G", "T"] if x != ref])
        large_variants.append(("22", pos, ref, alt))
    
    create_test_vcf("dev_docs/test_data/large_single_sample.vcf.gz", large_variants, ["SAMPLE1"])
    
    # Test Case 4: Population dataset with many samples
    print("4. Creating population dataset...")
    pop_variants = []
    for i in range(20):
        pos = 16000000 + (i * 25000)
        ref = random.choice(["A", "C", "G", "T"])
        alt = random.choice([x for x in ["A", "C", "G", "T"] if x != ref])
        pop_variants.append(("22", pos, ref, alt))
    
    sample_names = [f"SAMPLE{i:03d}" for i in range(1, 21)]
    create_test_vcf("dev_docs/test_data/population_20samples.vcf.gz", pop_variants, sample_names)
    
    # Test Case 5: Edge cases dataset
    print("5. Creating edge cases dataset...")
    edge_variants = [
        ("22", 16000001, "A", "T"),  # Very early position
        ("22", 50000000, "G", "C"),  # Late position
        ("22", 16500000, "AT", "A"), # Deletion
        ("22", 16600000, "G", "GA"), # Insertion
        ("22", 16700000, "CAT", "C"), # Complex deletion
    ]
    create_test_vcf("dev_docs/test_data/edge_cases.vcf.gz", edge_variants, ["SAMPLE1"])
    
    # Test Case 6: Multi-allelic variants
    print("6. Creating multi-allelic dataset...")
    # Note: For simplicity, we'll create separate bi-allelic variants
    # In real scenarios, multi-allelic variants would be more complex
    multiallelic_variants = [
        ("22", 16300000, "G", "A"),
        ("22", 16300000, "G", "T"),  # Same position, different alt
        ("22", 16400000, "C", "T"),
        ("22", 16500000, "A", "G"),
    ]
    create_test_vcf("dev_docs/test_data/multiallelic.vcf.gz", multiallelic_variants, ["SAMPLE1", "SAMPLE2"])
    
    # Create CSV files for batch processing tests
    print("7. Creating CSV batch files...")
    
    # Single sample CSV
    with open("dev_docs/test_data/single_sample.csv", "w") as f:
        f.write("sample_id,vcf_path\n")
        f.write("small_chr22,dev_docs/test_data/small_chr22.vcf.gz\n")

    # Multiple samples CSV
    with open("dev_docs/test_data/multiple_samples.csv", "w") as f:
        f.write("sample_id,vcf_path\n")
        f.write("small_chr22,dev_docs/test_data/small_chr22.vcf.gz\n")
        f.write("medium_multi,dev_docs/test_data/medium_multi_chr.vcf.gz\n")
        f.write("large_single,dev_docs/test_data/large_single_sample.vcf.gz\n")

    # Population study CSV
    with open("dev_docs/test_data/population_study.csv", "w") as f:
        f.write("sample_id,vcf_path\n")
        f.write("population_20,dev_docs/test_data/population_20samples.vcf.gz\n")
        f.write("edge_cases,dev_docs/test_data/edge_cases.vcf.gz\n")
        f.write("multiallelic,dev_docs/test_data/multiallelic.vcf.gz\n")
    
    # Create test scenarios documentation
    with open("dev_docs/test_data/TEST_SCENARIOS.md", "w") as f:
        f.write("""# Test Scenarios for vcf-liftover

## Generated Test Datasets

### 1. Small Dataset (small_chr22.vcf.gz)
- **Purpose**: Quick testing and validation
- **Variants**: 5 variants on chromosome 22
- **Samples**: 2 samples
- **Use case**: `--input dev_docs/test_data/small_chr22.vcf.gz`

### 2. Medium Multi-chromosome (medium_multi_chr.vcf.gz)
- **Purpose**: Test multi-chromosome processing
- **Variants**: 20 variants across chromosomes 21-22
- **Samples**: 3 samples
- **Use case**: `--input dev_docs/test_data/medium_multi_chr.vcf.gz`

### 3. Large Single Sample (large_single_sample.vcf.gz)
- **Purpose**: Performance testing with many variants
- **Variants**: 100 variants on chromosome 22
- **Samples**: 1 sample
- **Use case**: `--input dev_docs/test_data/large_single_sample.vcf.gz`

### 4. Population Dataset (population_20samples.vcf.gz)
- **Purpose**: Test with many samples
- **Variants**: 20 variants on chromosome 22
- **Samples**: 20 samples
- **Use case**: `--input dev_docs/test_data/population_20samples.vcf.gz`

### 5. Edge Cases (edge_cases.vcf.gz)
- **Purpose**: Test complex variants and edge positions
- **Variants**: 5 variants including indels
- **Samples**: 1 sample
- **Features**: Insertions, deletions, complex variants
- **Use case**: `--input dev_docs/test_data/edge_cases.vcf.gz`

### 6. Multi-allelic (multiallelic.vcf.gz)
- **Purpose**: Test multi-allelic variant handling
- **Variants**: 4 variants with overlapping positions
- **Samples**: 2 samples
- **Use case**: `--input dev_docs/test_data/multiallelic.vcf.gz`

## Batch Processing Tests

### CSV Input Tests
1. **Single sample**: `--input dev_docs/test_data/single_sample.csv`
2. **Multiple samples**: `--input dev_docs/test_data/multiple_samples.csv`
3. **Population study**: `--input dev_docs/test_data/population_study.csv`

### Wildcard Tests
1. **All VCF files**: `--input "dev_docs/test_data/*.vcf.gz"`
2. **Specific pattern**: `--input "dev_docs/test_data/small_*.vcf.gz"`

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
./nextflow run main.nf -profile test,singularity --input dev_docs/test_data/small_chr22.vcf.gz

# Multi-chromosome test
./nextflow run main.nf -profile test,singularity --input dev_docs/test_data/medium_multi_chr.vcf.gz

# Performance test
./nextflow run main.nf -profile test,singularity --input dev_docs/test_data/large_single_sample.vcf.gz

# Population test
./nextflow run main.nf -profile test,singularity --input dev_docs/test_data/population_20samples.vcf.gz

# Batch processing test
./nextflow run main.nf -profile test,singularity --input dev_docs/test_data/multiple_samples.csv

# Wildcard test
./nextflow run main.nf -profile test,singularity --input "dev_docs/test_data/small_*.vcf.gz"
```
""")
    
    print("\n✅ Test data generation complete!")
    print("\nGenerated files:")
    print("- small_chr22.vcf.gz (5 variants, 2 samples)")
    print("- medium_multi_chr.vcf.gz (20 variants, 3 samples)")
    print("- large_single_sample.vcf.gz (100 variants, 1 sample)")
    print("- population_20samples.vcf.gz (20 variants, 20 samples)")
    print("- edge_cases.vcf.gz (5 complex variants, 1 sample)")
    print("- multiallelic.vcf.gz (4 variants, 2 samples)")
    print("- single_sample.csv")
    print("- multiple_samples.csv")
    print("- population_study.csv")
    print("- TEST_SCENARIOS.md")

if __name__ == "__main__":
    main()
