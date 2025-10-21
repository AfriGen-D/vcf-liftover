# Resource Usage

Understanding and optimizing resource allocation for the VCF liftover pipeline.

## Default Resource Allocation

### Process-Specific Resources

| Process | CPUs | Memory | Time |
|---------|------|--------|------|
| VALIDATE_INPUT | 1 | 2 GB | 30m |
| GENERATE_CHR_MAPPING | 1 | 2 GB | 15m |
| CROSSMAP_LIFTOVER | 2 | 8 GB | 2h |
| SORT_AND_COMPRESS | 2 | 4 GB | 1h |
| INDEX_VCF | 1 | 2 GB | 30m |
| GENERATE_STATISTICS | 1 | 2 GB | 15m |
| GENERATE_REPORT | 1 | 2 GB | 15m |

## Scaling Resources

### For Large VCF Files

If processing whole-genome VCFs (>10GB):

**Option 1: Update nextflow.config**

```groovy
process {
  withName: 'CROSSMAP_LIFTOVER' {
    cpus   = 4
    memory = 16.GB
    time   = 4.h
  }

  withName: 'SORT_AND_COMPRESS' {
    cpus   = 4
    memory = 8.GB
    time   = 2.h
  }
}
```

**Option 2: Use command-line override**

```bash
nextflow run main.nf \
  --input large.vcf.gz \
  --target_fasta ref.fa \
  --max_memory 32.GB \
  --max_cpus 8 \
  -profile singularity
```

### For Small VCF Files

For targeted sequencing or exome data (<1GB):

```groovy
process {
  withName: 'CROSSMAP_LIFTOVER' {
    memory = 4.GB
    time   = 30.m
  }
}
```

## Resource Profiles

### Standard Profile

Default settings suitable for most use cases:
- Whole exome sequencing
- Targeted panels
- Moderate-sized whole genome data

### HPC Profile

Optimized for high-performance computing:

```bash
nextflow run main.nf -profile singularity,hpc
```

Features:
- Higher memory allocations
- Longer time limits
- Job scheduler integration

### Local Profile

For running on workstations:

```bash
nextflow run main.nf -profile docker,local
```

Features:
- Conservative resource requests
- Lower parallelization
- Suitable for testing

## Monitoring Resource Usage

### Real-Time Monitoring

```bash
nextflow run main.nf \
  -profile singularity \
  -with-trace \
  -with-report \
  -with-timeline
```

Generated files:
- `trace.txt` - Per-process resource usage
- `report.html` - Summary statistics
- `timeline.html` - Execution timeline

### Analyzing Resource Usage

After pipeline completion, review:

1. **Memory efficiency**: Check if processes used allocated memory
2. **CPU utilization**: Verify multi-threading efficiency
3. **I/O bottlenecks**: Identify slow file operations
4. **Time distribution**: Find slowest processes

## Optimization Tips

### Memory Optimization

1. **Reduce unnecessary memory**:
   - Review actual usage in `trace.txt`
   - Adjust allocations accordingly

2. **Enable dynamic retry**:
   ```groovy
   process {
     errorStrategy = { task.attempt < 3 ? 'retry' : 'finish' }
     memory = { 8.GB * task.attempt }
   }
   ```

### CPU Optimization

1. **Use appropriate parallelization**:
   - Most processes are single-threaded
   - Only CROSSMAP and SORT benefit from multiple CPUs

2. **Adjust based on data size**:
   - Small files: 1-2 CPUs sufficient
   - Large files: 4-8 CPUs beneficial

### Time Optimization

1. **Set realistic time limits**:
   - Too short: Jobs killed prematurely
   - Too long: Resources blocked unnecessarily

2. **Use resume efficiently**:
   ```bash
   nextflow run main.nf -resume
   ```

## Disk Space Requirements

### Temporary Storage

Nextflow work directory requires:
- **Input VCF size × 3-5**: Temporary files
- **Example**: 10GB VCF needs ~30-50GB scratch space

### Output Storage

Final outputs require:
- **Lifted VCF**: Similar to input size
- **Index files**: ~1-5% of VCF size
- **Reports**: <1MB per sample
- **Total**: ~110-120% of input size

### Cleanup

After successful completion:

```bash
# Remove work directory
rm -rf work/

# Or use Nextflow cleanup
nextflow clean -f
```

## Cloud Execution

### AWS Batch

```groovy
process {
  executor = 'awsbatch'
  queue = 'my-batch-queue'

  withName: 'CROSSMAP_LIFTOVER' {
    cpus = 4
    memory = 16.GB
  }
}
```

### Google Cloud

```groovy
process {
  executor = 'google-lifesciences'

  withName: 'CROSSMAP_LIFTOVER' {
    machineType = 'n1-standard-4'
  }
}
```

## Troubleshooting

### Out of Memory

**Symptom**: Process killed (exit code 137)

**Solution**: Increase memory allocation

### Timeout

**Symptom**: Process exceeds time limit

**Solution**: Increase time allocation or optimize process

### Disk Full

**Symptom**: "No space left on device"

**Solution**:
- Clean work directory
- Use different scratch location
- Increase available storage

## Best Practices

1. **Start conservative**: Use default settings first
2. **Monitor actual usage**: Check trace files
3. **Adjust incrementally**: Small increases at a time
4. **Document changes**: Note resource modifications
5. **Test at scale**: Validate with production data

## Next Steps

- [Process Flow](process-flow.md) - Understand execution order
- [Troubleshooting](/guide/troubleshooting) - Fix resource issues
