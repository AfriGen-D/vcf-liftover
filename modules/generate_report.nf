/*
========================================================================================
    Generate Reports Process
========================================================================================
    Produces both HTML and LaTeX PDF reports for the liftover pipeline.
    HTML report: interactive with tabs (summary, per-sample, rejection analysis, config)
    PDF report: archival/publication-quality from LaTeX
========================================================================================
*/

process GENERATE_REPORT {
    tag "report"
    label 'python'

    publishDir "${params.outdir}/reports", mode: 'copy'

    input:
    path picard_logs
    path rejected_summaries
    path nextflow_config

    output:
    path "liftover_report.html", emit: report
    path "liftover_report.pdf",  emit: pdf, optional: true
    path "liftover_report.tex",  emit: tex, optional: true

    script:
    def ver = workflow.manifest.version ?: '2.0.0'
    """
    # Generate HTML report
    generate_html_report.py \\
        --picard-logs ${picard_logs} \\
        --rejected-summaries ${rejected_summaries} \\
        --nextflow-config ${nextflow_config} \\
        --source-build ${params.source_build} \\
        --target-build ${params.target_build} \\
        --liftover-tool ${params.liftover_tool} \\
        --pipeline-version ${ver} \\
        --outdir ${params.outdir} \\
        --chain-file ${params.chain_file} \\
        --target-fasta ${params.target_fasta} \\
        --output liftover_report.html

    # Generate LaTeX PDF report (optional — requires tectonic or pdflatex)
    generate_latex_report.py \\
        --picard-logs ${picard_logs} \\
        --rejected-summaries ${rejected_summaries} \\
        --source-build ${params.source_build} \\
        --target-build ${params.target_build} \\
        --liftover-tool ${params.liftover_tool} \\
        --pipeline-version ${ver} \\
        --output liftover_report.tex || true

    if [ -f liftover_report.tex ]; then
        if command -v tectonic &> /dev/null; then
            tectonic liftover_report.tex || true
        elif command -v pdflatex &> /dev/null; then
            pdflatex -interaction=nonstopmode liftover_report.tex || true
            pdflatex -interaction=nonstopmode liftover_report.tex || true
        fi
    fi
    """
}
