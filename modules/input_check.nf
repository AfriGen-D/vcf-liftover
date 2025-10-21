/*
========================================================================================
    Input Validation Process
========================================================================================
    Validates input CSV file and checks VCF file existence
========================================================================================
*/

process INPUT_CHECK {
    tag "input_validation"
    label 'python'

    input:
    path input_csv

    output:
    path "validated_samples.csv", emit: csv

    script:
    """
    check_input.py \\
        --input ${input_csv} \\
        --output validated_samples.csv
    """
}
