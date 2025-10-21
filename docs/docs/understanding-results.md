# Understanding Results ​

Complete guide to interpreting vcf-liftover output files, statistics, and validation reports.

## Output Directory Structure ​

After a successful run, your results directory contains:

```
results/
├── vcf/                          # Lifted VCF files
│   ├── sample_lifted.vcf.gz      # Main output VCF
│   └── sample_lifted.vcf.gz.tbi  # Index file
├── reports/                      # Statistics and reports
│   ├── liftover_statistics.txt   # Summary statistics
│   ├── liftover_report.html      # Interactive report
│   └── pipeline_info/            # Execution details
├── logs/                         # Process logs
└── work/                         # Temporary files (can be deleted)
```

## Liftover Statistics ​

### Statistics File Format ​

The `liftover_statistics.txt` file provides comprehensive metrics:

```
vcf-liftover Statistics
==================================================
Generated: 2025-10-13 18:59:27
Source Build: hg19
Target Build: hg38

Summary Statistics:
  Total Samples: 3
  Total Input Variants: 10
  Total Output Variants: 8
  Total Unmapped Variants: 2
  Average Success Rate: 80.00%

Per-Sample Statistics:
  sample1:
    Input Variants: 5
    Output Variants: 4
    Success Rate: 80.00%

  sample2:
    Input Variants: 3
    Output Variants: 2
    Success Rate: 66.67%

  sample3:
    Input Variants: 2
    Output Variants: 2
    Success Rate: 100.00%
```

### Understanding Success Rates ​

#### Excellent (>98%) ​
- High-quality input data
- Standard chromosomes (1-22, X, Y)
- Well-annotated genomic regions

#### Good (95-98%) ​
- Typical for most genomic datasets
- Some variants in complex regions
- Minor assembly differences

#### Acceptable (90-95%) ​
- Older or lower-quality data
- Non-standard chromosome naming
- Variants in repetitive regions

#### Concerning (<90%) ​
- Check input data quality
- Verify correct source genome build
- Review chromosome naming conventions

## VCF Output Files ​

### Main Output VCF ​

The lifted VCF file contains converted coordinates:

**Before (hg19):**
```
##fileformat=VCFv4.2
##reference=hg19
#CHROM  POS       ID  REF ALT QUAL FILTER INFO
chr1    1000000   .   A   G   60   PASS   .
```

**After (hg38):**
```
##fileformat=VCFv4.2
##reference=GRCh38
#CHROM  POS       ID  REF ALT QUAL FILTER INFO
chr1    1064574   .   A   G   60   PASS   .
```

### Key Changes ​

1. **Coordinates updated** to target genome build
2. **Reference header** updated to reflect target
3. **Chromosome names** standardized if needed
4. **Sorting** by genomic position maintained

### Index Files ​

- `.tbi` files enable fast random access
- Required for most downstream tools
- Automatically generated for all outputs

## Interactive HTML Report ​

### Report Sections ​

#### Summary Dashboard ​
- Overall success rate visualization
- Chromosome-wise statistics
- Quality control status indicators

#### Detailed Statistics ​
- Variant count tables
- Success rate by chromosome
- Failure reason breakdown

#### Quality Control ​
- Input validation results
- Output file verification
- Process execution summary

#### Technical Details ​
- Pipeline version information
- Parameter settings used
- Execution timeline

### Interpreting Visualizations ​

#### Success Rate Chart ​
- Green bars: High success (>95%)
- Yellow bars: Moderate success (90-95%)
- Red bars: Low success (<90%)

#### Chromosome Distribution ​
- Shows variant density across chromosomes
- Identifies problematic regions
- Highlights assembly differences

## Validation Results ​

### Automatic Validation ​

The pipeline performs comprehensive validation:

#### Input Validation ​
- ✅ VCF format compliance
- ✅ File integrity checks
- ✅ Chromosome name verification
- ✅ Coordinate range validation

#### Process Validation ​
- ✅ CrossMap execution success
- ✅ Coordinate conversion accuracy
- ✅ Output file generation
- ✅ Sorting verification

#### Output Validation ​
- ✅ VCF format compliance
- ✅ Index file creation
- ✅ Chromosome naming consistency
- ✅ Position sorting verification

### Validation Flags ​

#### PASS ​
All validation checks completed successfully.

#### WARNING ​
Minor issues detected but processing continued:
- Non-standard chromosome names
- Missing INFO fields
- Format inconsistencies

#### FAIL ​
Critical issues that may affect results:
- Corrupted input files
- Incompatible genome builds
- Processing errors

## Common Result Patterns ​

### High Success Rate (>95%) ​

**Characteristics:**
- Standard chromosome naming (chr1, chr2, etc.)
- High-quality input data
- Variants in well-mapped regions

**Example output:**
```
Success rate: 97.8%
Failed variants: 2.2%
Primary failure: No target region (1.8%)
```

### Moderate Success Rate (85-95%) ​

**Characteristics:**
- Mixed chromosome naming
- Some variants in complex regions
- Older reference assemblies

**Example output:**
```
Success rate: 91.2%
Failed variants: 8.8%
Primary failure: Multiple mappings (4.2%)
```

### Low Success Rate (<85%) ​

**Possible causes:**
- Incorrect source genome build
- Non-standard chromosome naming
- Poor input data quality

**Troubleshooting steps:**
1. Verify input genome build
2. Check chromosome naming conventions
3. Validate input VCF format
4. Review chain file compatibility

## Failure Analysis ​

### Common Failure Reasons ​

#### No Target Region ​
- Variant position not in chain file
- Sequence not present in target genome
- Assembly-specific regions

#### Multiple Mappings ​
- Ambiguous coordinate conversion
- Repetitive sequence regions
- Structural variations

#### Chain Gap ​
- Gaps in the chain file alignment
- Assembly differences
- Unresolved genomic regions

### Investigating Failures ​

#### Check Failed Variants ​
```bash
# Extract failed variants (if available)
grep "FAIL" results/logs/crossmap.log

# Compare input vs output variant counts
zcat input.vcf.gz | grep -v "^#" | wc -l
zcat results/vcf/output_lifted.vcf.gz | grep -v "^#" | wc -l
```

#### Analyze Failure Patterns ​
- Are failures clustered in specific chromosomes?
- Do failures occur in known problematic regions?
- Are failure rates consistent across samples?

## Quality Control Recommendations ​

### Before Analysis ​
1. **Verify success rate** meets your requirements (typically >90%)
2. **Check chromosome coverage** for completeness
3. **Review failure patterns** for systematic issues
4. **Validate critical variants** manually if needed

### After Analysis ​
1. **Compare variant counts** between input and output
2. **Spot-check coordinates** for accuracy
3. **Verify downstream compatibility** with your tools
4. **Document any filtering decisions**

## Troubleshooting Results ​

### Low Success Rates ​

#### Check Input Data ​
```bash
# Verify VCF format
bcftools view -h input.vcf.gz | head -20

# Check chromosome names
bcftools view input.vcf.gz | cut -f1 | sort | uniq -c
```

#### Verify Parameters ​
```bash
# Confirm source genome build
--source_build hg19  # or hg38, GRCh37, etc.

# Check target reference
--target_fasta /path/to/correct/reference.fa
```

### Missing Output Files ​

#### Check Pipeline Logs ​
```bash
# Review execution logs
cat .nextflow.log

# Check process-specific logs
ls -la work/*/
```

#### Verify Permissions ​
```bash
# Check output directory permissions
ls -la results/

# Verify write access
touch results/test_file && rm results/test_file
```

## Best Practices ​

### Result Interpretation ​
1. **Always review statistics** before proceeding
2. **Understand your data** and expected success rates
3. **Document any quality issues** for reproducibility
4. **Validate critical regions** manually if needed

### Quality Thresholds ​
- **Production data**: Aim for >95% success rate
- **Research data**: >90% typically acceptable
- **Exploratory analysis**: >80% may be sufficient
- **Critical variants**: Manual validation recommended

### Downstream Considerations ​
1. **Update analysis pipelines** to use lifted coordinates
2. **Verify tool compatibility** with output format
3. **Document coordinate system** in metadata
4. **Consider impact** on existing annotations

## Related Resources ​

- [Liftover Methods](/docs/liftover-methods) - Understanding the conversion process
- [Quality Control](/docs/quality-control) - Comprehensive QC procedures
- [Troubleshooting](/docs/troubleshooting) - Solving common issues
- [Parameters](/reference/parameters) - Adjusting quality settings
