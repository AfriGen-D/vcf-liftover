# Input Files

This guide explains the input file requirements and formats for {{ PROJECT_NAME }}.

## Sample Sheet Format

### Required Format

The sample sheet must be a CSV file with the following columns:

| Column | Type | Description | Required |
|--------|------|-------------|----------|
| `sample` | string | Unique sample identifier | ✓ |
| `fastq_1` | path | Path to R1 FASTQ file | ✓ |
| `fastq_2` | path | Path to R2 FASTQ file (PE only) | * |

**Example:**
```csv
sample,fastq_1,fastq_2
sample1,/path/to/sample1_R1.fastq.gz,/path/to/sample1_R2.fastq.gz
sample2,/path/to/sample2_R1.fastq.gz,/path/to/sample2_R2.fastq.gz
```

### Single-End Data

For single-end sequencing, leave `fastq_2` empty:

```csv
sample,fastq_1,fastq_2
sample1,/path/to/sample1.fastq.gz,
sample2,/path/to/sample2.fastq.gz,
```

## File Requirements

### FASTQ Files
- **Format**: Compressed FASTQ (.fastq.gz)
- **Quality**: Illumina quality scores (Phred+33)
- **Naming**: Any naming convention supported
- **Size**: No specific limits (pipeline handles large files)

### Path Specifications
- Use absolute paths when possible
- Relative paths resolved from launch directory
- Network paths (NFS, S3) supported
- Wildcards not supported in sample sheet

## Validation

The pipeline automatically validates:
- File existence and accessibility
- FASTQ format integrity
- Sample ID uniqueness
- Required columns presence

## Advanced Configuration

### Multiple Libraries per Sample

For samples with multiple libraries:

```csv
sample,fastq_1,fastq_2,library
sample1,/path/to/sample1_lib1_R1.fastq.gz,/path/to/sample1_lib1_R2.fastq.gz,lib1
sample1,/path/to/sample1_lib2_R1.fastq.gz,/path/to/sample1_lib2_R2.fastq.gz,lib2
```

### Sample Groups

To specify sample groups for analysis:

```csv
sample,fastq_1,fastq_2,group
sample1,/path/to/sample1_R1.fastq.gz,/path/to/sample1_R2.fastq.gz,case
sample2,/path/to/sample2_R1.fastq.gz,/path/to/sample2_R2.fastq.gz,control
```