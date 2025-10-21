# Reference Overview ​

Complete command-line reference for vcf-liftover. This section provides comprehensive documentation for all parameters, profiles, and configuration options.

## Quick Reference ​

### Basic Command Structure ​

```bash
nextflow run main.nf [OPTIONS] [PARAMETERS]
```

### Essential Parameters ​

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--input` | ✅ | Input VCF file or CSV file with sample information |
| `--target_fasta` | ✅ | Target reference genome FASTA file (e.g., GRCh38) |
| `--outdir` | ❌ | Output directory (default: `results`) |

### Common Usage Patterns ​

```bash
# Single VCF file
nextflow run main.nf \
  --input sample.vcf.gz \
  --target_fasta GRCh38.fa \
  -profile singularity

# Multiple files via CSV
nextflow run main.nf \
  --input samples.csv \
  --target_fasta GRCh38.fa \
  -profile singularity

# With custom output directory
nextflow run main.nf \
  --input sample.vcf.gz \
  --target_fasta GRCh38.fa \
  --outdir my_results \
  -profile singularity
```

## Reference Sections ​

### [Parameters](/reference/parameters) ​
Complete documentation of all command-line parameters including:
- Input/Output parameters
- Liftover configuration options
- Processing parameters
- Quality control settings
- Resource allocation options

### [Profiles](/reference/profiles) ​
Available execution profiles for different environments:
- Container profiles (Docker, Singularity)
- Executor profiles (local, SLURM, PBS)
- Test profiles for validation
- Custom profile configuration

### [Configuration](/reference/configuration) ​
Advanced configuration options including:
- Custom configuration files
- Resource requirements
- Container settings
- Executor configuration
- Pipeline customization

## Parameter Categories ​

### Core Parameters ​
Essential parameters required for basic pipeline operation:
- Input file specification
- Reference genome configuration
- Output directory settings

### Liftover Parameters ​
Options specific to coordinate conversion:
- Source and target genome builds
- Chain file configuration
- Conversion validation settings

### Processing Parameters ​
Control how files are processed:
- VCF sorting and indexing
- Chromosome renaming
- Output compression
- Validation options

### Resource Parameters ​
Configure computational resources:
- CPU allocation
- Memory limits
- Execution time limits
- Process-specific resources

## Configuration Examples ​

### Basic Configuration ​

```bash
nextflow run main.nf \
  --input input.vcf.gz \
  --target_fasta GRCh38.fa \
  -profile singularity
```

### Advanced Configuration ​

```bash
nextflow run main.nf \
  --input samples.csv \
  --target_fasta GRCh38.fa \
  --source_build hg19 \
  --target_build hg38 \
  --validate_output true \
  --max_cpus 16 \
  --max_memory '64.GB' \
  -profile singularity
```

### Configuration File ​

```yaml
# nextflow.config
params {
  input = 'samples.csv'
  target_fasta = '/path/to/GRCh38.fa'
  outdir = 'results'
  source_build = 'hg19'
  target_build = 'hg38'
  validate_output = true
}

process {
  cpus = 4
  memory = '16.GB'
  time = '2.h'
}
```

## Profile Usage ​

### Container Profiles ​

```bash
# Use Singularity containers
-profile singularity

# Use Docker containers  
-profile docker

# Use Conda environments
-profile conda
```

### Executor Profiles ​

```bash
# Run locally
-profile local

# Submit to SLURM
-profile slurm

# Submit to PBS
-profile pbs
```

### Combined Profiles ​

```bash
# Singularity + SLURM
-profile singularity,slurm

# Docker + local execution
-profile docker,local
```

## Validation and Testing ​

### Test Profile ​

```bash
# Run with test data
nextflow run main.nf -profile test,singularity
```

### Validation Options ​

```bash
# Enable output validation
--validate_output true

# Skip validation for faster processing
--validate_output false
```

## Getting Help ​

### Command-Line Help ​

```bash
# Show all parameters
nextflow run main.nf --help

# Show specific parameter information
nextflow run main.nf --help | grep input
```

### Parameter Validation ​

The pipeline automatically validates:
- Required parameters are provided
- File paths exist and are accessible
- Parameter values are within valid ranges
- Configuration consistency

### Common Issues ​

- **Missing required parameters**: Use `--help` to see all required options
- **Invalid file paths**: Ensure all input files exist and are readable
- **Resource limits**: Adjust `--max_cpus` and `--max_memory` for your system
- **Profile conflicts**: Don't combine incompatible profiles

## Next Steps ​

- Review detailed [Parameters](/reference/parameters) documentation
- Learn about [Profiles](/reference/profiles) for your environment
- Explore [Configuration](/reference/configuration) options
- Try the [Tutorials](/tutorials/) for hands-on practice
