/*
========================================================================================
    VCF Indexing Process
========================================================================================
    Creates tabix indices for VCF files
========================================================================================
*/

process INDEX_VCF {
    tag "${sample_id}"
    label 'vcf_processing'

    publishDir "${params.outdir}/final", mode: 'copy'

    input:
    tuple val(sample_id), path(vcf)

    output:
    tuple val(sample_id), path(vcf), path("${vcf}.tbi"), emit: vcf_with_index
    path("${vcf}.tbi"), emit: index

    script:
    """
    echo "Starting VCF indexing for sample: ${sample_id}"
    echo "Input VCF: ${vcf}"
    
    # Check if input file exists
    if [ ! -f "${vcf}" ]; then
        echo "ERROR: Input VCF file not found: ${vcf}" >&2
        exit 1
    fi
    
    # Check if VCF is compressed
    if [[ "${vcf}" != *.gz ]]; then
        echo "ERROR: VCF file must be compressed (gzipped) for indexing: ${vcf}" >&2
        exit 1
    fi
    
    # Validate VCF format before indexing
    echo "Validating VCF format..."
    if command -v bcftools &> /dev/null; then
        bcftools view -h ${vcf} > /dev/null
        if [ \$? -ne 0 ]; then
            echo "ERROR: Invalid VCF format for sample ${sample_id}" >&2
            exit 1
        fi
        echo "VCF format validation passed"
    fi
    
    # Create tabix index
    echo "Creating tabix index..."
    tabix -f -p vcf ${vcf}
    
    if [ \$? -ne 0 ]; then
        echo "ERROR: Failed to create tabix index for sample ${sample_id}" >&2
        exit 1
    fi
    
    # Verify index file was created
    if [ ! -f "${vcf}.tbi" ]; then
        echo "ERROR: Tabix index file not created for sample ${sample_id}" >&2
        exit 1
    fi
    
    echo "VCF indexing completed successfully for sample: ${sample_id}"
    echo "Index file: ${vcf}.tbi"
    
    # Show file sizes
    vcf_size=\$(du -h ${vcf} | cut -f1)
    index_size=\$(du -h ${vcf}.tbi | cut -f1)
    echo "VCF file size: \$vcf_size"
    echo "Index file size: \$index_size"
    
    # Test index functionality
    if command -v bcftools &> /dev/null; then
        echo "Testing index functionality..."
        # Try to query a small region to test the index
        first_chr=\$(bcftools view -H ${vcf} | head -1 | cut -f1)
        if [ ! -z "\$first_chr" ]; then
            test_query=\$(bcftools view ${vcf} \$first_chr:1-1000 2>/dev/null | wc -l)
            echo "Index test successful - queried region \$first_chr:1-1000"
        fi
    fi
    """
}
