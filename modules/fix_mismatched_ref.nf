/*
========================================================================================
    Fix Mismatched Reference Alleles
========================================================================================
    Runs `bcftools +fixref` against the SOURCE build's reference fasta to flip
    REF/ALT where alleles are swapped on different strands. Variants that
    cannot be flipped (genuinely different REF allele) are dropped. Use this
    when picard's built-in --RECOVER_SWAPPED_REF_ALT is not enough and
    FILTER_REJECTED reports a high MismatchedRefAllele rate.

    Only runs when params.fix_mismatched_ref=true; otherwise the workflow
    skips this process entirely.
========================================================================================
*/

process FIX_MISMATCHED_REF {
    tag "${sample_id}"
    label 'vcf_processing'

    input:
    tuple val(sample_id), path(vcf)
    path source_fasta

    output:
    tuple val(sample_id), path("${sample_id}.fixref.vcf.gz"), emit: vcf
    path("${sample_id}.fixref.log"),                            emit: log

    script:
    """
    set -o pipefail

    echo "Running bcftools +fixref for sample: ${sample_id}"
    echo "Source reference: ${source_fasta}"

    # Step 1: report current state (check-only, no transform)
    echo "=== fixref pre-flight check ===" | tee ${sample_id}.fixref.log
    bcftools +fixref ${vcf} -- -f ${source_fasta} 2>&1 | tee -a ${sample_id}.fixref.log

    # Step 2: flip swappable strand-mismatched variants; drop unfixable
    echo "" | tee -a ${sample_id}.fixref.log
    echo "=== flipping / dropping ===" | tee -a ${sample_id}.fixref.log
    bcftools +fixref ${vcf} \\
        -Oz -o ${sample_id}.fixref.vcf.gz \\
        -- -f ${source_fasta} -m flip -d \\
        2>&1 | tee -a ${sample_id}.fixref.log

    bcftools index -t ${sample_id}.fixref.vcf.gz
    """
}
