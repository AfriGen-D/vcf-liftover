# Parameters Reference

Complete reference for all pipeline parameters in vcf-liftover.

## Input/Output Parameters

### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `--input` | `string` | Path to VCF file or CSV file with sample information |
| `--target_fasta` | `string` | Path to target reference genome FASTA file (e.g., GRCh38) |

### Optional I/O Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--outdir` | `string` | `'results'` | Output directory for results |
| `--chain_file` | `string` | `null` | Path to chain file (auto-downloaded if not provided) |
| `--validate_output` | `boolean` | `true` | Validate output VCF files |

## Liftover Parameters

### Core Liftover Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--source_build` | `string` | `'hg19'` | Source genome build |
| `--target_build` | `string` | `'hg38'` | Target genome build |
| `--chain_url` | `string` | `'https://hgdownload.cse.ucsc.edu/goldenpath/hg19/liftOver/hg19ToHg38.over.chain.gz'` | URL for chain file download |

## Processing Parameters

### VCF Processing Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--sort_vcf` | `boolean` | `true` | Sort output VCF files |
| `--rename_chromosomes` | `boolean` | `true` | Rename chromosomes to match target reference |
| `--fix_contigs` | `boolean` | `true` | Fix contig headers in VCF files |
| `--index_vcf` | `boolean` | `true` | Index output VCF files |

### Quality Control Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--generate_stats` | `boolean` | `true` | Generate liftover statistics |
| `--create_reports` | `boolean` | `true` | Create HTML and CSV reports |
| `--skip_validation` | `boolean` | `false` | Skip VCF validation |

### Output Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--publish_mode` | `string` | `'copy'` | File publishing mode (copy, symlink, move) |
| `--compress_output` | `boolean` | `true` | Compress output VCF files |

## Resource Parameters

### Computational Resources

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--max_cpus` | `integer` | `16` | Maximum number of CPUs |
| `--max_memory` | `string` | `128.GB` | Maximum memory allocation |
| `--max_time` | `string` | `240.h` | Maximum execution time |

### Process-Specific Resources

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--crossmap_cpus` | `integer` | `4` | CPUs for CrossMap liftover |
| `--crossmap_memory` | `string` | `16.GB` | Memory for CrossMap liftover |
| `--sort_cpus` | `integer` | `2` | CPUs for VCF sorting |
| `--sort_memory` | `string` | `8.GB` | Memory for VCF sorting |

## Advanced Parameters

### Container Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--singularity_pull_docker_container` | `boolean` | `false` | Pull Singularity from Docker Hub |
| `--docker_registry` | `string` | `'quay.io'` | Docker registry to use |

### Reporting Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--multiqc_config` | `string` | `null` | Custom MultiQC config file |
| `--multiqc_title` | `string` | `null` | Custom MultiQC report title |
| `--custom_config_version` | `string` | `'master'` | nf-core/configs version |

### Execution Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--custom_config_base` | `string` | `null` | Custom config base directory |
| `--hostnames` | `string` | `null` | Institutional config hostname |
| `--config_profile_name` | `string` | `null` | Institutional config name |
| `--config_profile_description` | `string` | `null` | Institutional config description |

## Parameter Files

### YAML Format

```yaml
# params.yml
input: 'input.vcf.gz'
target_fasta: '/path/to/GRCh38.fa'
outdir: 'results/'
source_build: 'hg19'
target_build: 'hg38'
validate_output: true
max_cpus: 16
max_memory: '64.GB'
```

### JSON Format

```json
{
  "input": "input.vcf.gz",
  "target_fasta": "/path/to/GRCh38.fa",
  "outdir": "results/",
  "source_build": "hg19",
  "target_build": "hg38",
  "validate_output": true,
  "max_cpus": 16,
  "max_memory": "64.GB"
}
```

## Parameter Validation

The pipeline validates parameters to ensure:

- Required parameters are provided
- File paths exist and are accessible
- Numeric values are within valid ranges
- Boolean values are properly formatted
- Memory/time specifications use valid units

### Common Validation Errors

**Missing required parameter:**
```
ERROR ~ Parameter '--input' is required but was not provided
```

**Invalid file path:**
```
ERROR ~ Input file does not exist: /path/to/missing/file.csv
```

**Invalid memory format:**
```
ERROR ~ Invalid memory specification: '64GB' (should be '64.GB')
```

## Examples

### Basic Parameter Set

```bash
nextflow run main.nf \
  --input input.vcf.gz \
  --target_fasta /path/to/GRCh38.fa \
  --outdir results/
```

### Advanced Parameter Set

```bash
nextflow run main.nf \
  --input input.vcf.gz \
  --target_fasta /path/to/GRCh38.fa \
  --outdir results/ \
  --source_build hg19 \
  --target_build hg38 \
  --validate_output true \
  --max_cpus 32 \
  --max_memory '128.GB'
```

### CSV Batch Processing

```bash
nextflow run main.nf \
  --input samples.csv \
  --target_fasta /path/to/GRCh38.fa \
  --outdir results/
```

For complete examples, see the [Examples section](/examples/).