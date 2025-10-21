# Quick Start

This guide will help you run {{ PROJECT_NAME }} with your own data.

## Basic Usage

The most basic command to run the pipeline:

```bash
nextflow run main.nf --input samples.csv --outdir results/
```

## Input Requirements

### Sample Sheet Format

Create a CSV file with your input samples:

```csv
sample,fastq_1,fastq_2
sample1,/path/to/sample1_R1.fastq.gz,/path/to/sample1_R2.fastq.gz
sample2,/path/to/sample2_R1.fastq.gz,/path/to/sample2_R2.fastq.gz
```

For single-end data, leave `fastq_2` empty:

```csv
sample,fastq_1,fastq_2
sample1,/path/to/sample1.fastq.gz,
sample2,/path/to/sample2.fastq.gz,
```

### {{ INPUT_TYPE_SPECIFIC }}

{{ INPUT_REQUIREMENTS }}

## Running Examples

### Example 1: Basic Run

```bash
nextflow run main.nf \
  --input samples.csv \
  --outdir results/ \
  --genome {{ DEFAULT_GENOME }}
```

### Example 2: With Custom Parameters

```bash
nextflow run main.nf \
  --input samples.csv \
  --outdir results/ \
  --genome {{ DEFAULT_GENOME }} \
  --{{ CUSTOM_PARAM1 }} {{ CUSTOM_VALUE1 }} \
  --{{ CUSTOM_PARAM2 }} {{ CUSTOM_VALUE2 }}
```

### Example 3: Using a Configuration File

Create a `params.yml` file:

```yaml
input: 'samples.csv'
outdir: 'results/'
genome: '{{ DEFAULT_GENOME }}'
{{ CUSTOM_PARAM1 }}: {{ CUSTOM_VALUE1 }}
{{ CUSTOM_PARAM2 }}: {{ CUSTOM_VALUE2 }}
```

Run with the config:

```bash
nextflow run main.nf -params-file params.yml
```

## Execution Profiles

### Local Execution

```bash
# Using Docker (default)
nextflow run main.nf --input samples.csv --outdir results/

# Using Singularity
nextflow run main.nf --input samples.csv --outdir results/ -profile singularity

# Using Conda
nextflow run main.nf --input samples.csv --outdir results/ -profile conda
```

### HPC Execution

```bash
# SLURM cluster
nextflow run main.nf --input samples.csv --outdir results/ -profile slurm

# PBS/Torque cluster
nextflow run main.nf --input samples.csv --outdir results/ -profile pbs
```

### Cloud Execution

```bash
# AWS Batch
nextflow run main.nf --input samples.csv \
  --outdir s3://your-bucket/results/ \
  -profile awsbatch

# Google Cloud Life Sciences
nextflow run main.nf --input samples.csv \
  --outdir gs://your-bucket/results/ \
  -profile gls
```

## Monitoring Progress

### Real-time Monitoring

Watch the pipeline progress:

```bash
# In another terminal
tail -f .nextflow.log
```

### Nextflow Tower

For advanced monitoring, use Nextflow Tower:

```bash
nextflow run main.nf --input samples.csv --outdir results/ \
  -with-tower
```

## Expected Outputs

After successful completion, you'll find:

```
results/
├── {{ OUTPUT_DIR1 }}/          # {{ OUTPUT_DESC1 }}
├── {{ OUTPUT_DIR2 }}/          # {{ OUTPUT_DESC2 }}
├── {{ OUTPUT_DIR3 }}/          # {{ OUTPUT_DESC3 }}
├── multiqc/
│   └── multiqc_report.html     # Quality control report
└── pipeline_info/
    ├── execution_report.html   # Nextflow execution report
    ├── execution_timeline.html # Timeline of job execution
    └── execution_trace.txt     # Detailed process information
```

## Common Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--input` | Path to sample sheet CSV | Required |
| `--outdir` | Output directory | `./results` |
| `--genome` | Reference genome | `{{ DEFAULT_GENOME }}` |
| `--{{ PARAM1 }}` | {{ PARAM1_DESC }} | `{{ PARAM1_DEFAULT }}` |
| `--{{ PARAM2 }}` | {{ PARAM2_DESC }} | `{{ PARAM2_DEFAULT }}` |

For a complete list, see the [Parameters reference](/api/parameters).

## Resuming Interrupted Runs

If your pipeline is interrupted, you can resume from where it left off:

```bash
nextflow run main.nf --input samples.csv --outdir results/ -resume
```

## Getting Help

- Check the [troubleshooting guide](/guide/troubleshooting) for common issues
- View [example configurations](/examples/) for different use cases
- Submit issues on [GitHub](https://github.com/AfriGen-D/{{ REPO_NAME }}/issues)