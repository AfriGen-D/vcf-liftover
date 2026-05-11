/*
========================================================================================
    Filter Rejected Variants Process
========================================================================================
    Analyzes and summarizes variants rejected during Picard LiftoverVcf
========================================================================================
*/

process FILTER_REJECTED {
    tag "${sample_id}"
    label 'vcf_processing'

    publishDir "${params.outdir}/rejected", mode: 'copy'

    input:
    tuple val(sample_id), path(rejected_vcf)

    output:
    tuple val(sample_id), path("${sample_id}.rejected_summary.txt"), emit: summary

    script:
    """
    echo "=== Rejected Variants Summary: ${sample_id} ===" > ${sample_id}.rejected_summary.txt
    echo "" >> ${sample_id}.rejected_summary.txt

    # Total rejected count
    total=\$(bcftools view -H ${rejected_vcf} 2>/dev/null | wc -l || echo "0")
    echo "Total rejected variants: \$total" >> ${sample_id}.rejected_summary.txt

    if [ "\$total" -gt 0 ]; then
        # Count by type
        snps=\$(bcftools view -H -v snps ${rejected_vcf} 2>/dev/null | wc -l || echo "0")
        indels=\$(bcftools view -H -v indels ${rejected_vcf} 2>/dev/null | wc -l || echo "0")
        echo "SNPs: \$snps" >> ${sample_id}.rejected_summary.txt
        echo "Indels: \$indels" >> ${sample_id}.rejected_summary.txt

        # Count by filter reason (from Picard FILTER field)
        echo "" >> ${sample_id}.rejected_summary.txt
        echo "Rejection reasons:" >> ${sample_id}.rejected_summary.txt
        bcftools query -f '%FILTER\\n' ${rejected_vcf} 2>/dev/null | sort | uniq -c | sort -rn >> ${sample_id}.rejected_summary.txt
    fi

    echo "" >> ${sample_id}.rejected_summary.txt
    echo "=== End Summary ===" >> ${sample_id}.rejected_summary.txt

    cat ${sample_id}.rejected_summary.txt
    """
}
