# Configuration Guide ​

Complete guide for configuring vcf-liftover with your reference files and system settings.

## Quick Setup ​

### 1. Download Reference Files ​

First, download the required reference files:

```bash
# Create directories
mkdir -p chains references

# Download chain files
wget -P chains/ http://hgdownload.cse.ucsc.edu/goldenpath/hg19/liftOver/hg19ToHg38.over.chain.gz
wget -P chains/ http://hgdownload.cse.ucsc.edu/goldenpath/hg38/liftOver/hg38ToHg19.over.chain.gz

# Download reference genomes
wget -O references/hg38.fa.gz http://hgdownload.cse.ucsc.edu/goldenpath/hg38/bigZips/hg38.fa.gz
gunzip references/hg38.fa.gz
samtools faidx references/hg38.fa
```

### 2. Create Configuration File ​

Create a configuration file with your file paths:

```bash
cat > my_liftover.config << 'EOF'
params {
    // Reference files (update these paths)
    target_fasta = '/full/path/to/references/hg38.fa'
    chain_file = '/full/path/to/chains/hg19ToHg38.over.chain.gz'
    
    // Output settings
    outdir = 'results'
    
    // Processing options
    validate_output = true
    min_success_rate = 0.90
}
EOF
```

### 3. Run Pipeline ​

```bash
nextflow run main.nf \
    --input your_variants.vcf.gz \
    -c my_liftover.config \
    -profile singularity
```

## Configuration Methods ​

### Method 1: Configuration File (Recommended) ​

Create a dedicated configuration file:

**liftover.config:**
```groovy
params {
    // Reference files
    target_fasta = '/data/references/hg38.fa'
    chain_file = '/data/chains/hg19ToHg38.over.chain.gz'
    
    // Output
    outdir = 'results'
    
    // Quality control
    validate_output = true
    min_success_rate = 0.90
    
    // Resources
    max_memory = '64.GB'
    max_cpus = 8
}
```

**Usage:**
```bash
nextflow run main.nf --input data.vcf.gz -c liftover.config -profile singularity
```

### Method 2: Command Line Parameters ​

Specify parameters directly:

```bash
nextflow run main.nf \
    --input your_variants.vcf.gz \
    --target_fasta /data/references/hg38.fa \
    --chain_file /data/chains/hg19ToHg38.over.chain.gz \
    --outdir results \
    -profile singularity
```

### Method 3: Environment Variables ​

Set environment variables:

```bash
export LIFTOVER_REFERENCE="/data/references/hg38.fa"
export LIFTOVER_CHAIN="/data/chains/hg19ToHg38.over.chain.gz"

nextflow run main.nf \
    --input your_variants.vcf.gz \
    --target_fasta $LIFTOVER_REFERENCE \
    --chain_file $LIFTOVER_CHAIN \
    -profile singularity
```

## Configuration Templates ​

### Basic Template ​

For simple single-file processing:

```groovy
params {
    // Required: Reference files
    target_fasta = '/path/to/hg38.fa'
    chain_file = '/path/to/chains/hg19ToHg38.over.chain.gz'
    
    // Optional: Output settings
    outdir = 'results'
    
    // Optional: Quality control
    validate_output = true
    min_success_rate = 0.90
}
```

### Production Template ​

For production environments:

```groovy
params {
    // Reference files
    target_fasta = '/data/references/GRCh38/hg38.fa'
    chain_file = '/data/chains/hg19ToHg38.over.chain.gz'
    
    // Output settings
    outdir = 'liftover_results'
    
    // Quality control
    validate_output = true
    min_success_rate = 0.95
    generate_report = true
    
    // Resource limits
    max_memory = '128.GB'
    max_cpus = 16
    max_time = '48.h'
    
    // Processing options
    crossmap_memory = '32.GB'
    sort_memory = '16.GB'
}

process {
    // Default resources
    cpus = 2
    memory = '8.GB'
    time = '4.h'
    
    // Specific process resources
    withName: CROSSMAP_LIFTOVER {
        cpus = 4
        memory = '16.GB'
        time = '8.h'
    }
    
    withName: SORT_VCF {
        cpus = 2
        memory = '8.GB'
        time = '2.h'
    }
}
```

### Cluster Template ​

For SLURM/PBS clusters:

```groovy
params {
    // Reference files
    target_fasta = '/shared/references/hg38.fa'
    chain_file = '/shared/chains/hg19ToHg38.over.chain.gz'
    
    // Output
    outdir = '/scratch/user/liftover_results'
    
    // Quality control
    validate_output = true
    min_success_rate = 0.90
    
    // Resource limits
    max_memory = '256.GB'
    max_cpus = 32
    max_time = '72.h'
}

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

## Reference File Configuration ​

### Required Files ​

| Parameter | Description | Example |
|-----------|-------------|---------|
| `target_fasta` | Target reference genome | `/data/hg38.fa` |
| `chain_file` | Liftover chain file | `/data/hg19ToHg38.over.chain.gz` |

### Optional Files ​

| Parameter | Description | Default |
|-----------|-------------|---------|
| `chr_mapping` | Chromosome name mapping | `null` |
| `reference_dict` | Reference dictionary | Auto-generated |

### File Path Guidelines ​

**Use absolute paths:**
```groovy
// Good
target_fasta = '/full/path/to/hg38.fa'

// Avoid relative paths
target_fasta = '../references/hg38.fa'
```

**Verify file existence:**
```bash
# Check files exist before running
ls -la /path/to/hg38.fa
ls -la /path/to/chains/hg19ToHg38.over.chain.gz
```

## Common Configurations ​

### hg19 to hg38 (Default) ​

```groovy
params {
    target_fasta = '/data/references/hg38.fa'
    chain_file = '/data/chains/hg19ToHg38.over.chain.gz'
    source_build = 'hg19'
    target_build = 'hg38'
}
```

### hg38 to hg19 (Reverse) ​

```groovy
params {
    target_fasta = '/data/references/hg19.fa'
    chain_file = '/data/chains/hg38ToHg19.over.chain.gz'
    source_build = 'hg38'
    target_build = 'hg19'
}
```

### Custom Genome Builds ​

```groovy
params {
    target_fasta = '/data/references/custom_genome.fa'
    chain_file = '/data/chains/source_to_target.over.chain.gz'
    source_build = 'custom_source'
    target_build = 'custom_target'
}
```

## Validation ​

### Check Configuration ​

Before running the pipeline, validate your configuration:

```bash
# Test configuration syntax
nextflow config -c my_config.config

# Check file paths
nextflow run main.nf --help -c my_config.config

# Dry run to validate
nextflow run main.nf \
    --input test_data/small_chr22.vcf.gz \
    -c my_config.config \
    -profile singularity \
    -preview
```

### Common Issues ​

**File not found errors:**
```bash
# Check file permissions
ls -la /path/to/reference/files/

# Verify absolute paths
realpath /path/to/hg38.fa
```

**Memory issues:**
```groovy
// Increase memory limits
params {
    max_memory = '128.GB'
    crossmap_memory = '64.GB'
}
```

## Related Documentation ​

- [Parameters Reference](/reference/parameters) - Complete parameter list
- [Quick Start Tutorial](/tutorials/quick-start) - Step-by-step setup
- [Examples](/examples/) - Configuration examples
- [Troubleshooting](/docs/troubleshooting) - Common issues
