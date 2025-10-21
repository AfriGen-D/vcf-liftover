# Output Files

The VCF liftover pipeline generates several output files organized in the specified output directory.

## Directory Structure

```
results/
├── lifted_vcfs/          # Lifted over VCF files
├── statistics/           # Liftover statistics
├── reports/              # HTML reports
└── logs/                 # Process logs
```

## Main Output Files

### Lifted VCF Files

**Location**: `results/lifted_vcfs/`

- `<sample>.lifted.vcf.gz` - Lifted over VCF file (bgzipped)
- `<sample>.lifted.vcf.gz.tbi` - Tabix index file
- `<sample>.unlifted.vcf.gz` - Variants that could not be lifted (if any)

### Statistics

**Location**: `results/statistics/`

- `<sample>.stats.txt` - Liftover statistics including:
  - Total variants
  - Successfully lifted variants
  - Failed variants
  - Success rate percentage

### Reports

**Location**: `results/reports/`

- `<sample>.report.html` - Comprehensive HTML report with:
  - Summary statistics
  - Quality control metrics
  - Chromosome-wise breakdown
  - Visualizations

## Understanding Results

### Success Rates

A typical successful liftover has:
- **>95% success rate**: Excellent liftover
- **90-95% success rate**: Good liftover
- **<90% success rate**: Review input data quality

### Common Issues

Low success rates may indicate:
- Incorrect chain file for genome builds
- Poor quality input VCF
- Chromosome naming mismatches (usually auto-corrected)

## Next Steps

- [Troubleshooting](/guide/troubleshooting) - Fix common issues
- [Understanding Results](/docs/understanding-results) - Interpret the output
