# Examples ​

Practical examples for running vcf-liftover in different scenarios, from simple single-file processing to complex multi-sample studies.

## Prerequisites ​

### Download Required Files ​

Before running any examples, you'll need reference files:

```bash
# Download chain files
mkdir -p chains
wget -P chains/ http://hgdownload.cse.ucsc.edu/goldenpath/hg19/liftOver/hg19ToHg38.over.chain.gz
wget -P chains/ http://hgdownload.cse.ucsc.edu/goldenpath/hg38/liftOver/hg38ToHg19.over.chain.gz

# Download GRCh38 reference genome (~3GB)
wget http://hgdownload.cse.ucsc.edu/goldenpath/hg38/bigZips/hg38.fa.gz
gunzip hg38.fa.gz
samtools faidx hg38.fa

# For hg19 reference (if needed for reverse liftover)
wget http://hgdownload.cse.ucsc.edu/goldenpath/hg19/bigZips/hg19.fa.gz
gunzip hg19.fa.gz
samtools faidx hg19.fa
```

**Alternative: Use pre-built test files for quick examples:**

The repository includes pre-built test files that are much smaller and faster for testing.

### Download Test Data ​

If test data is not available locally:

```bash
# Create test data directory
mkdir -p test_data

# Download essential test files
wget -P test_data/ https://github.com/AfriGen-D/vcf-liftover/raw/main/test_data/small_chr22.vcf.gz
wget -P test_data/ https://github.com/AfriGen-D/vcf-liftover/raw/main/test_data/GRCh38_test_regions.fa
wget -P test_data/ https://github.com/AfriGen-D/vcf-liftover/raw/main/test_data/GRCh38_test_regions.fa.fai
wget -P test_data/ https://github.com/AfriGen-D/vcf-liftover/raw/main/test_data/samples.csv

# Verify download
ls -lh test_data/
```

### Verify Test Data ​

```bash
# Check available test files (if repository was cloned)
ls -lh test_data/*.vcf.gz
ls -lh test_data/*.fa

# Check available test scenarios
cat test_data/README.md
```

## Quick Start Examples ​

### Single VCF File ​

The simplest way to lift over a single VCF file:

```bash
# Basic liftover from hg19 to hg38
nextflow run main.nf \
    --input my_variants.vcf.gz \
    --target_fasta hg38.fa \
    --chain_file chains/hg19ToHg38.over.chain.gz \
    -profile singularity
```

**What this does:**

- Converts coordinates from hg19 to hg38 (default)
- Uses Singularity containers for reproducibility
- Outputs results to `results/` directory

### With Custom Output Directory ​

```bash
nextflow run main.nf \
    --input my_variants.vcf.gz \
    --target_fasta hg38.fa \
    --chain_file chains/hg19ToHg38.over.chain.gz \
    --outdir liftover_results \
    -profile singularity
```

### Test Run with Sample Data ​

```bash
# Use built-in test data
nextflow run main.nf -profile test,singularity

# Use pre-built test data (included in repository)
nextflow run main.nf \
    --input test_data/small_chr22.vcf.gz \
    --target_fasta test_data/GRCh38_test_regions.fa \
    --chain_file chains/hg19ToHg38.test.chain.gz \
    -profile singularity
```

## Batch Processing Examples ​

### Multiple Files with CSV Input ​

Create a CSV file listing your samples:

```csv
sample_id,vcf_path
sample1,/data/vcf/sample1.vcf.gz
sample2,/data/vcf/sample2.vcf.gz
sample3,/data/vcf/sample3.vcf.gz
```

Then run the pipeline:

```bash
nextflow run main.nf \
    --input samples.csv \
    --target_fasta hg38.fa \
    --chain_file chains/hg19ToHg38.over.chain.gz \
    --outdir batch_results \
    -profile singularity
```

### Population Study (20+ Samples) ​

For large-scale studies using pre-built test data:

```bash
# Use pre-built population test data (included in repository)
nextflow run main.nf \
    --input test_data/population_study.csv \
    --target_fasta hg38.fa \
    --chain_file chains/hg19ToHg38.over.chain.gz \
    --outdir population_liftover \
    --max_memory 64.GB \
    --max_cpus 16 \
    -profile singularity
```

## Computing Environment Examples ​

### Local Machine with Docker ​

```bash
nextflow run main.nf \
    --input my_variants.vcf.gz \
    --target_fasta hg38.fa \
    --chain_file chains/hg19ToHg38.over.chain.gz \
    -profile docker
```

### SLURM Cluster ​

```bash
nextflow run main.nf \
    --input samples.csv \
    --target_fasta hg38.fa \
    --chain_file chains/hg19ToHg38.over.chain.gz \
    --max_memory 256.GB \
    --max_cpus 32 \
    -profile singularity,slurm \
    -w /scratch/work
```

### High-Memory Node ​

For very large VCF files:

```bash
nextflow run main.nf \
    --input large_cohort.vcf.gz \
    --target_fasta hg38.fa \
    --chain_file chains/hg19ToHg38.over.chain.gz \
    --crossmap_memory 128.GB \
    --sort_memory 64.GB \
    -profile singularity
```

## Genome Build Conversions ​

### hg19 to hg38 (Default) ​

```bash
nextflow run main.nf \
    --input variants_hg19.vcf.gz \
    --target_fasta GRCh38.fa \
    --source_build hg19 \
    --target_build hg38 \
    -profile singularity
```

### hg38 to hg19 (Reverse) ​

```bash
nextflow run main.nf \
    --input variants_hg38.vcf.gz \
    --target_fasta hg19.fa \
    --chain_file chains/hg38ToHg19.over.chain.gz \
    --source_build hg38 \
    --target_build hg19 \
    -profile singularity
```

### Custom Chain File ​

```bash
nextflow run main.nf \
    --input variants.vcf.gz \
    --target_fasta custom_reference.fa \
    --chain_file /path/to/custom.over.chain.gz \
    --source_build custom_source \
    --target_build custom_target \
    -profile singularity
```

## Quality Control Examples ​

### With Validation Enabled ​

```bash
nextflow run main.nf \
    --input variants.vcf.gz \
    --target_fasta GRCh38.fa \
    --validate_output true \
    --min_success_rate 0.90 \
    -profile singularity
```

### Skip Validation for Speed ​

```bash
nextflow run main.nf \
    --input variants.vcf.gz \
    --target_fasta GRCh38.fa \
    --validate_output false \
    --skip_stats false \
    -profile singularity
```

## Advanced Configuration Examples ​

### Custom Resource Allocation ​

```bash
nextflow run main.nf \
    --input large_dataset.csv \
    --target_fasta GRCh38.fa \
    --crossmap_cpus 8 \
    --crossmap_memory 32.GB \
    --sort_cpus 4 \
    --sort_memory 16.GB \
    -profile singularity
```

### Chromosome Renaming ​

```bash
nextflow run main.nf \
    --input variants.vcf.gz \
    --target_fasta GRCh38.fa \
    --chr_mapping assets/chr_mapping.txt \
    --rename_chromosomes true \
    -profile singularity
```

**chr_mapping.txt example:**

```
1 chr1
2 chr2
3 chr3
X chrX
Y chrY
MT chrM
```

## Real-World Use Cases ​

### GWAS Study Liftover ​

```bash
# Lift over GWAS results from hg19 to hg38
nextflow run main.nf \
    --input gwas_results.csv \
    --target_fasta GRCh38.fa \
    --outdir gwas_hg38 \
    --validate_output true \
    --generate_report true \
    -profile singularity,slurm
```

### Multi-Cohort Analysis ​

```csv
sample_id,vcf_path
cohort1_sample1,/data/cohort1/sample1.vcf.gz
cohort1_sample2,/data/cohort1/sample2.vcf.gz
cohort2_sample1,/data/cohort2/sample1.vcf.gz
cohort2_sample2,/data/cohort2/sample2.vcf.gz
```

```bash
nextflow run main.nf \
    --input multi_cohort.csv \
    --target_fasta GRCh38.fa \
    --outdir multi_cohort_hg38 \
    --max_memory 128.GB \
    --max_cpus 24 \
    -profile singularity,slurm
```

### Clinical Variant Analysis ​

```bash
# High-confidence liftover for clinical variants
nextflow run main.nf \
    --input clinical_variants.vcf.gz \
    --target_fasta GRCh38.fa \
    --validate_output true \
    --min_success_rate 0.95 \
    --generate_detailed_stats true \
    --outdir clinical_hg38 \
    -profile singularity
```

## Testing and Development ​

### Quick Test Run ​

```bash
# Test with minimal data
nextflow run main.nf -profile test,singularity
```

### Use Pre-Built Test Data ​

```bash
# Test with pre-built comprehensive datasets (included in repository)
nextflow run main.nf \
    --input test_data/medium_multi_chr.vcf.gz \
    --target_fasta test_data/GRCh38_test_regions.fa \
    -profile singularity

# Test different scenarios
nextflow run main.nf \
    --input test_data/edge_cases.vcf.gz \
    --target_fasta test_data/GRCh38_test_regions.fa \
    -profile singularity
```

### Development Mode ​

```bash
# Run with detailed logging and reports
nextflow run main.nf \
    --input test_data/small_chr22.vcf.gz \
    --target_fasta test_data/GRCh38_test_regions.fa \
    -profile singularity \
    -with-trace \
    -with-report \
    -with-timeline \
    -with-dag flowchart.html
```

## Troubleshooting Examples ​

### Resume Failed Run ​

```bash
# Resume from where it left off
nextflow run main.nf \
    --input samples.csv \
    --target_fasta GRCh38.fa \
    -profile singularity \
    -resume
```

### Debug Low Success Rate ​

```bash
# Run with detailed logging
nextflow run main.nf \
    --input problematic.vcf.gz \
    --target_fasta GRCh38.fa \
    --validate_output true \
    --debug_mode true \
    -profile singularity
```

### Memory Issues ​

```bash
# Increase memory for large files
nextflow run main.nf \
    --input large_file.vcf.gz \
    --target_fasta GRCh38.fa \
    --crossmap_memory 64.GB \
    --sort_memory 32.GB \
    --max_memory 128.GB \
    -profile singularity
```

## Configuration Files ​

### Basic Configuration ​

Create a configuration file with your downloaded reference files:

**my_liftover.config:**

```groovy
params {
    // Reference files (update these paths to your downloaded files)
    target_fasta = '/full/path/to/hg38.fa'
    chain_file = '/full/path/to/chains/hg19ToHg38.over.chain.gz'

    // Output settings
    outdir = 'results'

    // Processing options
    validate_output = true
    min_success_rate = 0.90

    // Resource limits (adjust for your system)
    max_memory = '64.GB'
    max_cpus = 8
    max_time = '24.h'
}
```

**Usage:**

```bash
nextflow run main.nf \
    --input your_variants.vcf.gz \
    -c my_liftover.config \
    -profile singularity
```

### Advanced Configuration ​

**production.config:**

```groovy
params {
    // Input/Output
    input = null
    outdir = 'results'

    // Reference files (update these paths)
    target_fasta = '/data/references/hg38.fa'
    chain_file = '/data/chains/hg19ToHg38.over.chain.gz'

    // Processing options
    validate_output = true
    min_success_rate = 0.90

    // Resource limits
    max_memory = '128.GB'
    max_cpus = 16
    max_time = '240.h'
}

process {
    withName: CROSSMAP_LIFTOVER {
        cpus = 4
        memory = '16.GB'
        time = '4.h'
    }

    withName: SORT_VCF {
        cpus = 2
        memory = '8.GB'
        time = '2.h'
    }
}
```

### Cluster Configuration ​

**slurm.config:**

```groovy
process {
    executor = 'slurm'
    queue = 'normal'
    
    withLabel: process_low {
        cpus = 2
        memory = '4.GB'
        time = '2.h'
    }
    
    withLabel: process_medium {
        cpus = 4
        memory = '16.GB'
        time = '8.h'
    }
    
    withLabel: process_high {
        cpus = 8
        memory = '32.GB'
        time = '24.h'
    }
}
```

For more detailed information, see:

- [Parameters Reference](/reference/parameters) - Complete parameter documentation
- [Profiles Reference](/reference/profiles) - Execution environment configurations
- [Tutorials](/tutorials/) - Step-by-step learning guides
- [Understanding Results](/docs/understanding-results) - Output interpretation
