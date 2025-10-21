/*
========================================================================================
    Liftover Statistics Process
========================================================================================
    Generates comprehensive statistics and reports for the liftover process
========================================================================================
*/

process LIFTOVER_STATS {
    tag "liftover_statistics"
    label 'python'

    publishDir "${params.outdir}/reports", mode: 'copy'

    input:
    path crossmap_logs
    path final_vcfs

    output:
    path "liftover_summary_report.html", emit: report
    path "liftover_statistics.txt", emit: stats
    path "sample_summary.csv", emit: csv

    script:
    """
    generate_liftover_stats.py \\
        --source-build ${params.source_build} \\
        --target-build ${params.target_build} \\
        --chain-file ${params.chain_file} \\
        --target-fasta ${params.target_fasta} \\
        --chr-mapping "${params.chr_mapping}" \\
        --outdir ${params.outdir}
    """
}
