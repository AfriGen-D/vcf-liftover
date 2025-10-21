/*
========================================================================================
    Chromosome Validation Process
========================================================================================
    Validates that chromosomes in VCF files exist in the target reference genome.
    Catches common issues like wrong reference or chromosome naming mismatches.
========================================================================================
*/

process VALIDATE_CHROMOSOMES {
    tag "chromosome_validation"
    label 'python'
    errorStrategy 'terminate'  // Fail immediately if chromosomes don't match

    input:
    path input_csv
    path target_fasta
    path target_fasta_fai

    output:
    path "${input_csv}", emit: csv

    script:
    """
    validate_chromosomes.py \\
        --input ${input_csv} \\
        --target-fasta ${target_fasta}
    """
}
