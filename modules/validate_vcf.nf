/*
========================================================================================
    VCF Validation Process
========================================================================================
    Validates output VCF files for format compliance and data integrity
========================================================================================
*/

process VALIDATE_VCF {
    tag "${sample_id}"
    label 'python'

    publishDir "${params.outdir}/validation", mode: 'copy'

    input:
    tuple val(sample_id), path(vcf), path(index)

    output:
    path("${sample_id}.validation_report.txt"), emit: report

    when:
    params.validate_output

    script:
    """
    validate_vcf.py \\
        --sample-id ${sample_id} \\
        --vcf ${vcf} \\
        --index ${index} \\
        --output ${sample_id}.validation_report.txt
    """
}
