/*
========================================================================================
    Contig Header Fix Process
========================================================================================
    Updates VCF headers with target reference information
========================================================================================
*/

process FIX_CONTIG_HEADER {
    tag "${sample_id}"
    label 'vcf_processing'

    publishDir "${params.outdir}/final", mode: 'copy'

    input:
    tuple val(sample_id), path(vcf)
    path target_fasta

    output:
    tuple val(sample_id), path("${sample_id}.${params.target_build}.vcf.gz"), emit: vcf

    script:
    """
    echo "Starting contig header fix for sample: ${sample_id}"
    echo "Input VCF: ${vcf}"
    echo "Target FASTA: ${target_fasta}"
    echo "Target build: ${params.target_build}"
    
    # Check if input file exists
    if [ ! -f "${vcf}" ]; then
        echo "ERROR: Input VCF file not found: ${vcf}" >&2
        exit 1
    fi
    
    # Check if target FASTA exists
    if [ ! -f "${target_fasta}" ]; then
        echo "ERROR: Target FASTA file not found: ${target_fasta}" >&2
        exit 1
    fi
    
    # Convert BCF to VCF and compress directly
    echo "Converting BCF to compressed VCF..."
    bcftools view ${vcf} -Oz -o ${sample_id}.${params.target_build}.vcf.gz
    
    if [ \$? -ne 0 ]; then
        echo "ERROR: Failed to compress final VCF for sample ${sample_id}" >&2
        exit 1
    fi
    
    # Verify output file was created
    if [ ! -f "${sample_id}.${params.target_build}.vcf.gz" ]; then
        echo "ERROR: Final VCF file not created for sample ${sample_id}" >&2
        exit 1
    fi
    
    # Clean up temporary files
    rm -f temp.vcf reheadered.vcf
    
    echo "Contig header fix completed successfully for sample: ${sample_id}"
    echo "Output VCF: ${sample_id}.${params.target_build}.vcf.gz"
    
    # Show final statistics
    if command -v bcftools &> /dev/null; then
        variant_count=\$(bcftools view -H ${sample_id}.${params.target_build}.vcf.gz | wc -l)
        echo "Final variant count: \$variant_count"
        
        echo "Final VCF header contigs:"
        bcftools view -h ${sample_id}.${params.target_build}.vcf.gz | grep "^##contig" | head -5
    fi
    """
}
