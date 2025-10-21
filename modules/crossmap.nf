/*
========================================================================================
    CrossMap Liftover Process
========================================================================================
    Performs coordinate liftover using CrossMap
========================================================================================
*/

process CROSSMAP_VCF {
    tag "${sample_id}"
    label 'crossmap'

    publishDir "${params.outdir}/crossmap", mode: 'copy'

    input:
    tuple val(sample_id), path(vcf), path(chain_file), path(target_fasta)

    output:
    tuple val(sample_id), path("${sample_id}.crossmap.vcf"), emit: vcf
    path("${sample_id}.crossmap.log"), emit: log
    path("${sample_id}.crossmap.unmap"), emit: unmap, optional: true

    script:
    """
    echo "Starting CrossMap liftover for sample: ${sample_id}"
    echo "Input VCF: ${vcf}"
    echo "Chain file: ${chain_file}"
    echo "Target FASTA: ${target_fasta}"
    
    # Run CrossMap
    CrossMap vcf \\
        ${chain_file} \\
        ${vcf} \\
        ${target_fasta} \\
        ${sample_id}.crossmap.vcf \\
        2> ${sample_id}.crossmap.log

    # Check if CrossMap completed successfully
    if [ \$? -ne 0 ]; then
        echo "ERROR: CrossMap failed for sample ${sample_id}" >&2
        cat ${sample_id}.crossmap.log >&2
        exit 1
    fi

    # Check if output VCF was created
    if [ ! -f "${sample_id}.crossmap.vcf" ]; then
        echo "ERROR: CrossMap output VCF not created for sample ${sample_id}" >&2
        exit 1
    fi

    # Check if unmapped file was created and rename it
    if [ -f "${sample_id}.crossmap.vcf.unmap" ]; then
        mv "${sample_id}.crossmap.vcf.unmap" "${sample_id}.crossmap.unmap"
        echo "Unmapped variants file created: ${sample_id}.crossmap.unmap"
    fi

    # Log completion
    echo "CrossMap liftover completed successfully for sample: ${sample_id}"
    echo "Output VCF: ${sample_id}.crossmap.vcf"
    
    # Count variants in input and output
    if command -v bcftools &> /dev/null; then
        input_count=\$(bcftools view -H ${vcf} | wc -l)
        output_count=\$(bcftools view -H ${sample_id}.crossmap.vcf | wc -l)
        echo "Input variants: \$input_count"
        echo "Output variants: \$output_count"
        echo "Liftover success rate: \$(echo "scale=2; \$output_count / \$input_count * 100" | bc -l)%"
    fi
    """
}
