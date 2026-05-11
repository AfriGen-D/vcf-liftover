/*
========================================================================================
    Picard LiftoverVcf Process
========================================================================================
    Performs coordinate liftover using Picard LiftoverVcf.
    Unlike CrossMap, Picard correctly handles REF/ALT swaps when the reference
    allele changes between genome builds (--RECOVER_SWAPPED_REF_ALT true).

    Container requirements: picard + java only. Input VCF must be .vcf.gz
    (BCF→VCF prep happens upstream in PREPARE_VCF_FOR_PICARD). Variant
    counts happen downstream in COUNT_LIFTED_VARIANTS so the bcftools
    calls live in a container that actually has bcftools.
========================================================================================
*/

process PICARD_LIFTOVER {
    tag "${sample_id}"
    label 'picard'

    input:
    tuple val(sample_id), path(vcf), path(chain_file), path(target_fasta), path(target_fasta_fai), path(target_fasta_dict)

    output:
    tuple val(sample_id), path("${sample_id}.lifted.vcf.gz"), emit: vcf
    tuple val(sample_id), path("${sample_id}.rejected.vcf.gz"), emit: rejected
    tuple val(sample_id), path("${sample_id}.picard.log"), emit: log

    script:
    def java_mem = task.memory ? "-Xmx${Math.max(task.memory.toGiga() - 1, 1)}g" : "-Xmx2g"
    """
    set -o pipefail

    echo "Starting Picard LiftoverVcf for sample: ${sample_id}"
    echo "Input VCF: ${vcf}"
    echo "Chain file: ${chain_file}"
    echo "Target FASTA: ${target_fasta}"

    _JAVA_OPTIONS="${java_mem}" picard LiftoverVcf \\
        -I ${vcf} \\
        -O ${sample_id}.lifted.vcf.gz \\
        -C ${chain_file} \\
        -R ${target_fasta} \\
        --REJECT ${sample_id}.rejected.vcf.gz \\
        --RECOVER_SWAPPED_REF_ALT true \\
        --WRITE_ORIGINAL_POSITION true \\
        --WRITE_ORIGINAL_ALLELES true \\
        --VALIDATION_STRINGENCY LENIENT \\
        --MAX_RECORDS_IN_RAM 100000 \\
        2>&1 | tee ${sample_id}.picard.log

    echo "Picard LiftoverVcf completed for sample: ${sample_id}"
    """
}
