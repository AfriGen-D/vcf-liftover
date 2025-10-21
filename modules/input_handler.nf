/*
========================================================================================
    Input Handler Process
========================================================================================
    Handles multiple input types: single VCF, multiple VCFs, or CSV file
    Uses external Python script for processing
========================================================================================
*/

process INPUT_HANDLER {
    tag "input_processing"
    label 'python'
    errorStrategy 'terminate'  // Don't retry on errors - they're likely permanent (file not found, etc.)

    input:
    val input_param
    val launch_dir
    path script_file

    output:
    path "processed_samples.csv", emit: csv

    script:
    // Convert relative path to absolute path for CSV files
    def input_path = input_param
    if (input_param.toString().endsWith('.csv')) {
        input_path = file(input_param).toAbsolutePath()
    }
    """
    python3 ${script_file} "${input_path}" --launch-dir "${launch_dir}" -o processed_samples.csv
    """
}
