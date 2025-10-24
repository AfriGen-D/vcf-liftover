# Edge Case Testing Guide

Quick reference for testing validation enhancements.

## Quick Test Commands

### Run All Tests (Recommended)

```bash
cd /users/mamana/vcf-liftover
bash dev_docs/run_comprehensive_tests.sh
```

This runs:
- **4 functional tests** (normal VCF liftover scenarios)
- **9 validation edge case tests** (error detection scenarios)

Expected runtime: ~10-15 minutes (depending on container availability)

## Individual Edge Case Tests

### Test 1: Empty File Detection
```bash
./nextflow run main.nf \
    --input test_data/edge_cases/config/test_empty_file.csv \
    --target_fasta test_data/hg38/reference/hg38_chr22.fa \
    --chain chains/hg19ToHg38.over.chain.gz \
    -profile test,singularity
```
**Expected:** ❌ FAIL with "EMPTY VCF FILE" error

### Test 2: Corrupted Gzip Detection
```bash
./nextflow run main.nf \
    --input test_data/edge_cases/config/test_corrupted_gzip.csv \
    --target_fasta test_data/hg38/reference/hg38_chr22.fa \
    --chain chains/hg19ToHg38.over.chain.gz \
    -profile test,singularity
```
**Expected:** ❌ FAIL with "CORRUPTED GZIP" error

### Test 3: Build Mismatch Detection (CRITICAL)
```bash
./nextflow run main.nf \
    --input test_data/edge_cases/config/test_build_mismatch.csv \
    --target_fasta test_data/hg38/reference/hg38_chr22.fa \
    --chain chains/hg19ToHg38.over.chain.gz \
    -profile test,singularity
```
**Expected:** ❌ FAIL with "BUILD MISMATCH DETECTED" error
**Why Critical:** Prevents silent data corruption from wrong build liftover

### Test 4: Valid Control (Should Pass)
```bash
./nextflow run main.nf \
    --input test_data/edge_cases/config/test_valid_control.csv \
    --target_fasta test_data/hg38/reference/hg38_chr22.fa \
    --chain chains/hg19ToHg38.over.chain.gz \
    -profile test,singularity
```
**Expected:** ✅ PASS - successful liftover

## Test Standalone Validation Scripts

Test validation scripts directly without running the full workflow:

### Test Build Detection
```bash
# Detect build from hg19 VCF
python bin/detect_genome_build.py \
    --vcf test_data/edge_cases/vcf/valid_hg19.vcf.gz

# Detect build from hg38 VCF
python bin/detect_genome_build.py \
    --vcf test_data/edge_cases/vcf/hg38_mismatch.vcf.gz

# Detect build from reference
python bin/detect_genome_build.py \
    --reference test_data/hg38/reference/hg38_chr22.fa.fai
```

### Test Build Compatibility
```bash
# Test compatible scenario (should pass)
python bin/check_build_compatibility.py \
    --vcf test_data/edge_cases/vcf/valid_hg19.vcf.gz \
    --chain chains/hg19ToHg38.over.chain.gz \
    --target-ref test_data/hg38/reference/hg38_chr22.fa \
    --sample-id test1 \
    --output /tmp/compat_test.txt

cat /tmp/compat_test.txt

# Test incompatible scenario (should fail)
python bin/check_build_compatibility.py \
    --vcf test_data/edge_cases/vcf/hg38_mismatch.vcf.gz \
    --chain chains/hg19ToHg38.over.chain.gz \
    --target-ref test_data/hg38/reference/hg38_chr22.fa \
    --sample-id test2 \
    --output /tmp/compat_fail.txt

cat /tmp/compat_fail.txt
```

### Test Input Validation
```bash
# Test empty file detection
python bin/check_input.py \
    --input test_data/edge_cases/config/test_empty_file.csv \
    --output /tmp/validation_test.csv

# Test corrupted gzip detection
python bin/check_input.py \
    --input test_data/edge_cases/config/test_corrupted_gzip.csv \
    --output /tmp/validation_test.csv
```

## Understanding Test Results

### Comprehensive Test Script Output

The script provides colored output:
- 🟦 **[INFO]** - Informational messages
- 🟩 **[✓ SUCCESS]** - Test passed
- 🟥 **[✗ ERROR]** - Test failed
- 🟨 **[⚠ WARNING]** - Warning message
- 🟦 **[VALIDATION]** - Validation test header

### Expected Summary Output

```
════════════════════════════════════════════════════════════════════════════
                           TEST SUITE SUMMARY
════════════════════════════════════════════════════════════════════════════

[INFO] FUNCTIONAL TESTS:
[INFO]   Total tests run: 4
[✓ SUCCESS]   Tests passed: 4

[INFO] VALIDATION EDGE CASE TESTS:
[INFO]   Total tests run: 9
[✓ SUCCESS]   Tests passed: 9

────────────────────────────────────────────────────────────────────────────
[INFO] OVERALL RESULTS:
[INFO]   Total tests: 13
[✓ SUCCESS]   Passed: 13

════════════════════════════════════════════════════════════════════════════
                        🎉 ALL TESTS PASSED! 🎉
════════════════════════════════════════════════════════════════════════════

[INFO] The vcf-liftover pipeline is working correctly with:
[INFO]   ✓ All functional test scenarios
[INFO]   ✓ All validation edge cases
[INFO]   ✓ Proper error detection and handling
[INFO]   ✓ Graceful failure degradation
```

## Troubleshooting Test Failures

### Container Issues

If tests fail with "Failed to pull singularity image":
```bash
# Ensure Singularity is in PATH
export PATH=/software/common/singularity/4.2.2/bin:$PATH

# Manually pull container from node with internet
cd ~/.singularity
/software/common/singularity/4.2.2/bin/singularity pull \
    mamana-vcf-processing-latest.img \
    docker://mamana/vcf-processing:latest
```

### Check Test Logs

```bash
# View functional test logs
ls -lh test_*_*.log
cat test_1_small_dataset.log

# View validation test logs
ls -lh validation_*_*.log
cat validation_6_build_mismatch.log
```

### Verify Edge Case Files

```bash
# Check edge case files were created
ls -lh test_data/edge_cases/vcf/*.vcf.gz

# Should show:
# - empty.vcf.gz (0 bytes)
# - corrupted_gzip.vcf.gz (48 bytes)
# - valid_hg19.vcf.gz (227 bytes)
# etc.
```

## What Each Test Validates

| Test | Validates | Error Detected | Script |
|------|-----------|----------------|--------|
| empty_file | File size check | 0-byte files | check_input.py |
| tiny_file | File size check | Truncated files | check_input.py |
| corrupted_gzip | Gzip integrity | Corrupted compression | check_input.py |
| wrong_format | VCF format | Non-VCF files | check_input.py |
| no_variants | Data presence | Header-only VCFs | check_input.py |
| build_mismatch | Build compatibility | Wrong build liftover | check_build_compatibility.py |
| wrong_chromosomes | Chromosome validation | Missing chromosomes | validate_chromosomes.py |
| valid_control | All validations | Should pass | All scripts |
| mixed_samples | Graceful degradation | Partial failure handling | Workflow |

## Next Steps After Testing

1. **All tests pass** → Pipeline ready for production use
2. **Some tests fail** → Check logs and container setup
3. **Validation tests fail** → Verify Python scripts are executable

## References

- Full edge case documentation: [README.md](README.md)
- Implementation details: [../dev_docs/VALIDATION_IMPLEMENTATION_REPORT.md](../dev_docs/VALIDATION_IMPLEMENTATION_REPORT.md)
- Troubleshooting guide: [../docs/guide/troubleshooting.md](../docs/guide/troubleshooting.md)
