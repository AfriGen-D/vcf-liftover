# Running the Pipeline

## Basic Usage

Run the VCF liftover pipeline with minimal configuration:

```bash
nextflow run main.nf \
  --input input.vcf.gz \
  --target_fasta GRCh38.fa \
  --outdir results \
  -profile singularity
```

## Command Line Options

### Required Parameters

- `--input`: Path to input VCF file or CSV file with multiple VCFs
- `--target_fasta`: Path to target reference genome FASTA file
- `--outdir`: Output directory for results

### Optional Parameters

- `--chain`: Path to CrossMap chain file (auto-downloaded if not provided)
- `--chr_mapping`: Custom chromosome name mapping file
- `-profile`: Execution profile (singularity, docker, conda)

For a complete list of parameters, see the [Parameters Reference](/reference/parameters).

## Execution Profiles

### Singularity (HPC)

```bash
nextflow run main.nf -profile singularity --input data.vcf.gz --target_fasta ref.fa
```

### Docker (Local)

```bash
nextflow run main.nf -profile docker --input data.vcf.gz --target_fasta ref.fa
```

### Test Profile

```bash
nextflow run main.nf -profile test,singularity
```

## Resuming Failed Runs

If a pipeline run fails, you can resume from the last successful step:

```bash
nextflow run main.nf -profile singularity -resume
```

## Monitoring Progress

View real-time progress:

```bash
nextflow run main.nf -profile singularity -with-timeline -with-report -with-trace
```

This generates:
- `timeline.html` - Execution timeline
- `report.html` - Resource usage report
- `trace.txt` - Detailed execution trace

## Next Steps

- [Output Files](/guide/output-files) - Understand the results
- [Troubleshooting](/guide/troubleshooting) - Common issues and solutions
