# Troubleshooting

Common issues and solutions when running the VCF liftover pipeline.

## Pipeline Execution Issues

### Pipeline Fails to Start

**Symptom**: Pipeline fails immediately after launch

**Causes & Solutions**:

1. **Missing input file**
   ```bash
   # Verify file exists
   ls -lh input.vcf.gz
   ```

2. **Missing reference genome**
   ```bash
   # Check reference FASTA and index
   ls -lh reference.fa reference.fa.fai
   ```

3. **Container runtime not available**
   ```bash
   # Test Singularity
   singularity --version

   # Or Docker
   docker --version
   ```

### Out of Memory Errors

**Symptom**: Process killed due to memory limits

**Solution**: Increase memory allocation in `nextflow.config`:

```groovy
process {
  withName: 'CROSSMAP_LIFTOVER' {
    memory = '16.GB'
  }
}
```

### Disk Space Issues

**Symptom**: "No space left on device"

**Solution**:
```bash
# Check disk usage
df -h

# Clean Nextflow work directory
rm -rf work/
```

## Liftover Issues

### Low Success Rate

**Symptom**: <90% variants successfully lifted

**Causes & Solutions**:

1. **Wrong chain file**
   - Verify chain file matches genome builds
   - Example: hg19→hg38 requires `hg19ToHg38.over.chain.gz`

2. **Chromosome naming mismatch**
   - Usually auto-corrected
   - Manually verify with `--chr_mapping` if needed

3. **Poor quality input VCF**
   - Validate VCF format
   - Check for malformed records

### All Variants Fail to Lift

**Symptom**: 0% success rate

**Solution**:
```bash
# Check chromosome naming
zcat input.vcf.gz | grep -v "^#" | head -1

# Verify against reference
head reference.fa.fai
```

## Container Issues

### Singularity Pull Fails

**Symptom**: Cannot download Singularity image

**Solution**:
```bash
# Manually pull image
singularity pull docker://afrigend/crossmap:latest

# Use local cache
export NXF_SINGULARITY_CACHEDIR=/path/to/cache
```

### Docker Permission Denied

**Symptom**: Cannot connect to Docker daemon

**Solution**:
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Or use Singularity instead
nextflow run main.nf -profile singularity
```

## Resume Issues

### Resume Not Working

**Symptom**: Pipeline reruns all steps despite `-resume`

**Causes**:
- Work directory was deleted
- Input files changed
- Configuration changed

**Solution**:
```bash
# Ensure work/ directory exists
ls -la work/

# Use absolute paths for inputs
nextflow run main.nf --input /absolute/path/to/input.vcf.gz -resume
```

## Getting Help

If you encounter issues not covered here:

1. Check [GitHub Issues](https://github.com/AfriGen-D/vcf-liftover/issues)
2. Contact [Helpdesk](https://helpdesk.afrigen-d.org)
3. Review Nextflow logs in `.nextflow.log`

## Debug Mode

Run with detailed logging:

```bash
nextflow run main.nf \
  -profile singularity \
  -with-trace \
  -with-report \
  -with-timeline \
  --input data.vcf.gz \
  --target_fasta ref.fa
```

This generates diagnostic files:
- `trace.txt` - Detailed execution trace
- `report.html` - Resource usage
- `timeline.html` - Execution timeline
