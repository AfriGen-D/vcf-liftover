/*
========================================================================================
    VCF Sorting Process
========================================================================================
    Sorts VCF files using bcftools
========================================================================================
*/

process SORT_VCF {
    tag "${sample_id}"
    label 'vcf_processing'

    input:
    tuple val(sample_id), path(vcf)

    output:
    tuple val(sample_id), path("${sample_id}.sorted.vcf.gz"), emit: vcf

    script:
    """
    echo "Starting VCF sorting for sample: ${sample_id}"
    echo "Input VCF: ${vcf}"
    
    # Check if input file exists
    if [ ! -f "${vcf}" ]; then
        echo "ERROR: Input VCF file not found: ${vcf}" >&2
        exit 1
    fi
    
    # Create temporary directory for sorting
    mkdir -p tmp_sort
    
    # Convert to BCF and sort
    echo "Converting VCF to BCF format..."
    bcftools view ${vcf} -Oz -o temp.vcf.gz
    
    if [ \$? -ne 0 ]; then
        echo "ERROR: Failed to convert VCF to BCF for sample ${sample_id}" >&2
        exit 1
    fi
    
    echo "Sorting BCF file..."
    bcftools sort temp.vcf.gz -T tmp_sort -Oz -o ${sample_id}.sorted.vcf.gz
    
    if [ \$? -ne 0 ]; then
        echo "ERROR: Failed to sort BCF for sample ${sample_id}" >&2
        exit 1
    fi
    
    # Verify output file was created
    if [ ! -f "${sample_id}.sorted.vcf.gz" ]; then
        echo "ERROR: Sorted BCF file not created for sample ${sample_id}" >&2
        exit 1
    fi
    
    # Clean up temporary files
    rm -f temp.vcf.gz
    rm -rf tmp_sort
    
    echo "VCF sorting completed successfully for sample: ${sample_id}"
    echo "Output BCF: ${sample_id}.sorted.vcf.gz"
    
    # Count variants
    if command -v bcftools &> /dev/null; then
        variant_count=\$(bcftools view -H ${sample_id}.sorted.vcf.gz | wc -l)
        echo "Sorted variants: \$variant_count"
    fi
    """
}
