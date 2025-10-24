#!/bin/bash
# Create edge case test files for validation testing

EDGE_DIR="$(dirname "$0")"
cd "$EDGE_DIR"

echo "Creating edge case test VCF files..."

# 1. Empty VCF file (0 bytes)
echo "1. Creating empty.vcf.gz (0 bytes)..."
touch empty.vcf.gz

# 2. Tiny file (too small to be valid)
echo "2. Creating tiny_truncated.vcf.gz (truncated file)..."
echo "##fileformat=VCFv4.2" | gzip > tiny_truncated.vcf.gz

# 3. Corrupted gzip file
echo "3. Creating corrupted_gzip.vcf.gz (corrupted compression)..."
echo "This is not a gzip file at all" > corrupted_gzip.vcf.gz

# 4. Valid gzip but not VCF format (wrong format)
echo "4. Creating not_vcf_format.vcf.gz (wrong format)..."
cat > not_vcf_format.txt << 'VCF'
This is a text file
Not a VCF file
Sample,Data,Values
VCF
gzip not_vcf_format.txt
mv not_vcf_format.txt.gz not_vcf_format.vcf.gz

# 5. VCF header only (no data)
echo "5. Creating header_only.vcf.gz (no variants)..."
cat > header_only.vcf << 'VCF'
##fileformat=VCFv4.2
##reference=hg19
##contig=<ID=chr22,length=51304566>
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	SAMPLE1
VCF
bgzip -c header_only.vcf > header_only.vcf.gz
rm header_only.vcf

# 6. hg38 VCF (for build mismatch testing with hg19ToHg38 chain)
echo "6. Creating hg38_mismatch.vcf.gz (wrong build)..."
cat > hg38_mismatch.vcf << 'VCF'
##fileformat=VCFv4.2
##reference=file:///path/to/GRCh38.fa
##contig=<ID=chr22,length=50818468>
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	SAMPLE1
chr22	10500000	.	G	A	30	PASS	.	GT	0/1
chr22	10500100	.	C	T	30	PASS	.	GT	0/1
chr22	10500200	.	A	G	30	PASS	.	GT	0/1
VCF
bgzip -c hg38_mismatch.vcf > hg38_mismatch.vcf.gz
tabix -p vcf hg38_mismatch.vcf.gz
rm hg38_mismatch.vcf

# 7. Valid hg19 VCF (should pass all checks)
echo "7. Creating valid_hg19.vcf.gz (control - should pass)..."
cat > valid_hg19.vcf << 'VCF'
##fileformat=VCFv4.2
##reference=file:///path/to/hg19.fa
##contig=<ID=chr22,length=51304566>
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	SAMPLE1
chr22	16050000	.	G	A	30	PASS	.	GT	0/1
chr22	16050100	.	C	T	30	PASS	.	GT	0/1
chr22	16050200	.	A	G	30	PASS	.	GT	0/1
chr22	16050300	.	T	C	30	PASS	.	GT	0/1
chr22	16050400	.	G	T	30	PASS	.	GT	0/1
VCF
bgzip -c valid_hg19.vcf > valid_hg19.vcf.gz
tabix -p vcf valid_hg19.vcf.gz
rm valid_hg19.vcf

# 8. Chromosome mismatch (chromosomes not in reference)
echo "8. Creating wrong_chromosomes.vcf.gz (chromosomes not in reference)..."
cat > wrong_chromosomes.vcf << 'VCF'
##fileformat=VCFv4.2
##reference=file:///path/to/hg19.fa
##contig=<ID=chrZ,length=12345>
##contig=<ID=chrY,length=59373566>
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	SAMPLE1
chrZ	1000	.	G	A	30	PASS	.	GT	0/1
chrY	2600000	.	C	T	30	PASS	.	GT	0/1
VCF
bgzip -c wrong_chromosomes.vcf > wrong_chromosomes.vcf.gz
tabix -p vcf wrong_chromosomes.vcf.gz
rm wrong_chromosomes.vcf

# 9. Missing reference in header (unknown build)
echo "9. Creating unknown_build.vcf.gz (no build info)..."
cat > unknown_build.vcf << 'VCF'
##fileformat=VCFv4.2
##contig=<ID=chr22,length=51304566>
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	SAMPLE1
chr22	16050000	.	G	A	30	PASS	.	GT	0/1
VCF
bgzip -c unknown_build.vcf > unknown_build.vcf.gz
tabix -p vcf unknown_build.vcf.gz
rm unknown_build.vcf

echo "Edge case test files created successfully!"
ls -lh *.vcf.gz
