# Edge Case Test Data

Test files designed to validate all validation enhancements in the VCF liftover pipeline.

## Test Files

| File | Size | Purpose | Expected Validation Behavior |
|------|------|---------|------------------------------|
| `empty.vcf.gz` | 0 bytes | Empty file | ❌ **FAIL** - File size validation should detect empty file |
| `tiny_truncated.vcf.gz` | 41 bytes | Truncated VCF header | ❌ **FAIL** - File size validation (too small) |
| `corrupted_gzip.vcf.gz` | 48 bytes | Invalid gzip | ❌ **FAIL** - Gzip integrity test should detect corruption |
| `not_vcf_format.vcf.gz` | 103 bytes | CSV file, not VCF | ❌ **FAIL** - VCF format validation should detect wrong format |
| `header_only.vcf.gz` | 171 bytes | Valid VCF header, no variants | ❌ **FAIL** - Data presence check should detect no variants |
| `hg38_mismatch.vcf.gz` | 206 bytes | hg38 VCF | ❌ **FAIL** - Build compatibility (hg38 incompatible with hg19ToHg38 chain) |
| `wrong_chromosomes.vcf.gz` | 215 bytes | Chromosomes not in reference | ❌ **FAIL** - Chromosome validation should detect missing chromosomes |
| `unknown_build.vcf.gz` | 172 bytes | No reference in header | ⚠️ **WARN** - Build detection may return 'unknown', but should still process |
| `valid_hg19.vcf.gz` | 227 bytes | Valid hg19 VCF | ✅ **PASS** - All validations should pass |

## Validation Checks Tested

### 1. File Size Validation
**Tests:** `empty.vcf.gz`, `tiny_truncated.vcf.gz`

**Validates:**
- Detects 0-byte files
- Detects files too small to contain valid VCF data
- Script: `bin/check_input.py::check_file_size()`

**Expected Error Message:**
```
╔════════════════════════════════════════════════════════════════════════════╗
║                       ❌  EMPTY VCF FILE  ❌                                 ║
╚════════════════════════════════════════════════════════════════════════════╝

Sample: empty_file
File size: 0 bytes
```

### 2. Gzip Integrity Testing
**Tests:** `corrupted_gzip.vcf.gz`

**Validates:**
- Detects corrupted gzip compression
- Prevents crashes during bcftools processing
- Script: `bin/check_input.py::check_gzip_integrity()`

**Expected Error Message:**
```
╔════════════════════════════════════════════════════════════════════════════╗
║                      ❌  CORRUPTED GZIP FILE  ❌                             ║
╚════════════════════════════════════════════════════════════════════════════╝

Sample: corrupted_gzip
Gzip integrity test failed
```

### 3. VCF Format Validation
**Tests:** `not_vcf_format.vcf.gz`

**Validates:**
- Detects non-VCF files with .vcf.gz extension
- Uses bcftools to validate VCF format
- Script: `bin/check_input.py::check_vcf_format()`

**Expected Error Message:**
```
╔════════════════════════════════════════════════════════════════════════════╗
║                    ❌  INVALID VCF FORMAT  ❌                                ║
╚════════════════════════════════════════════════════════════════════════════╝

Sample: not_vcf
bcftools validation failed
```

### 4. Data Presence Check
**Tests:** `header_only.vcf.gz`

**Validates:**
- Detects VCF files with no variant records
- Prevents processing of empty datasets
- Script: `bin/check_input.py::check_vcf_has_data()`

**Expected Error Message:**
```
╔════════════════════════════════════════════════════════════════════════════╗
║                   ❌  NO VARIANTS IN VCF FILE  ❌                            ║
╚════════════════════════════════════════════════════════════════════════════╝

Sample: no_variants
VCF has valid header but no variant records
```

### 5. Build Compatibility Check
**Tests:** `hg38_mismatch.vcf.gz`

**Validates:**
- Detects genome build mismatches
- Prevents incorrect liftover results
- Script: `bin/check_build_compatibility.py`

**Test Scenario:**
- VCF: hg38 (already at target build)
- Chain: hg19ToHg38.over.chain.gz (expects hg19 input)
- Result: **INCOMPATIBLE** - would produce wrong results

**Expected Error Message:**
```
╔════════════════════════════════════════════════════════════════════════════╗
║                    ❌  BUILD MISMATCH DETECTED  ❌                           ║
╚════════════════════════════════════════════════════════════════════════════╝

VCF Build: hg38
Chain expects: hg19 → hg38

ERROR: VCF is already hg38, but chain expects hg19 input!
This would produce INCORRECT coordinates.
```

### 6. Chromosome Validation
**Tests:** `wrong_chromosomes.vcf.gz`

**Validates:**
- Detects chromosomes in VCF not present in reference genome
- Distinguishes naming differences (OK) from missing chromosomes (ERROR)
- Script: `bin/validate_chromosomes.py`

**Expected Error Message:**
```
╔════════════════════════════════════════════════════════════════════════════╗
║          ❌  CHROMOSOME MISMATCH - WRONG REFERENCE GENOME  ❌               ║
╚════════════════════════════════════════════════════════════════════════════╝

Sample: wrong_chr
VCF chromosomes: chrZ, chrW
Reference chromosomes: chr1, chr2, ..., chr22, chrX, chrY

Missing from reference: chrZ, chrW
```

### 7. Build Detection
**Tests:** `unknown_build.vcf.gz`

**Validates:**
- Attempts to detect genome build from VCF header
- Falls back to "unknown" if no build information available
- Script: `bin/detect_genome_build.py`

**Expected Behavior:**
- Build detected as "unknown"
- Warning logged but processing continues
- May still work if chromosomes are compatible

## Test Configuration Files

Located in `test_data/edge_cases/config/`:

| CSV File | Test Scenario | Expected Result |
|----------|---------------|-----------------|
| `test_empty_file.csv` | Single empty file | All samples fail validation |
| `test_corrupted_gzip.csv` | Single corrupted file | All samples fail validation |
| `test_wrong_format.csv` | Single wrong format file | All samples fail validation |
| `test_tiny_file.csv` | Single truncated file | All samples fail validation |
| `test_no_variants.csv` | Header only, no data | All samples fail validation |
| `test_build_mismatch.csv` | hg38 with wrong chain | Build compatibility fails |
| `test_wrong_chromosomes.csv` | Invalid chromosomes | Chromosome validation fails |
| `test_unknown_build.csv` | No build information | Warning, may continue |
| `test_valid_control.csv` | Valid hg19 VCF | ✅ All validations pass |
| `test_mixed_samples.csv` | Mix of valid and invalid | Some pass, some fail (graceful) |

## Running Edge Case Tests

### Individual Test Scenarios

```bash
# Test empty file detection
./nextflow run main.nf \
    --input test_data/edge_cases/config/test_empty_file.csv \
    --target_fasta test_data/hg38/reference/hg38_chr22.fa \
    --chain chains/hg19ToHg38.over.chain.gz \
    -profile singularity

# Test build mismatch detection
./nextflow run main.nf \
    --input test_data/edge_cases/config/test_build_mismatch.csv \
    --target_fasta test_data/hg38/reference/hg38_chr22.fa \
    --chain chains/hg19ToHg38.over.chain.gz \
    -profile singularity

# Test valid control (should pass)
./nextflow run main.nf \
    --input test_data/edge_cases/config/test_valid_control.csv \
    --target_fasta test_data/hg38/reference/hg38_chr22.fa \
    --chain chains/hg19ToHg38.over.chain.gz \
    -profile singularity
```

### Comprehensive Test Suite

```bash
# Run all edge case tests
bash dev_docs/run_comprehensive_tests.sh
```

## Expected Outcomes

### Files That Should FAIL Validation
1. ❌ `empty.vcf.gz` - Empty file error
2. ❌ `tiny_truncated.vcf.gz` - Too small error
3. ❌ `corrupted_gzip.vcf.gz` - Gzip integrity error
4. ❌ `not_vcf_format.vcf.gz` - Format validation error
5. ❌ `header_only.vcf.gz` - No variants error
6. ❌ `hg38_mismatch.vcf.gz` - Build compatibility error
7. ❌ `wrong_chromosomes.vcf.gz` - Chromosome validation error

### Files That Should PASS Validation
1. ✅ `valid_hg19.vcf.gz` - All checks pass
2. ⚠️ `unknown_build.vcf.gz` - May pass with warning (build unknown)

### Mixed Sample Behavior
When using `test_mixed_samples.csv`:
- Valid samples should proceed to liftover
- Invalid samples should be filtered out
- Workflow continues with valid samples only (graceful degradation)

## Validation Enhancements Summary

These test files validate the following enhancements:

1. **Visual Error Formatting** - ASCII box errors impossible to miss
2. **Multi-Level Validation** - File → Format → Content → Build
3. **Gzip Integrity Testing** - Prevents crashes from corrupted files
4. **Build Mismatch Prevention** - Critical for data accuracy
5. **Graceful Failure Handling** - Failed samples don't crash workflow
6. **Comprehensive Error Context** - Specific suggestions for resolution

## Troubleshooting

If tests don't behave as expected:

1. **Check validation is enabled:**
   ```bash
   # Ensure build checking is on (default)
   ./nextflow run main.nf --check_build_compatibility true
   ```

2. **View detailed error logs:**
   ```bash
   cat work/*/.*/.command.err
   cat test_results/build_reports/*_build_compatibility.txt
   ```

3. **Check Python scripts are executable:**
   ```bash
   ls -l bin/*.py | grep -E "check_input|detect_genome_build|check_build_compatibility"
   ```

## References

- Implementation Report: `dev_docs/VALIDATION_IMPLEMENTATION_REPORT.md`
- Technical Details: `dev_docs/validation_enhancements.md`
- User Documentation: `docs/guide/troubleshooting.md`
