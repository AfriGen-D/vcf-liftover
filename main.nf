#!/usr/bin/env nextflow

/*
========================================================================================
    vcf-liftover
========================================================================================
    Nextflow pipeline for lifting over VCF files between genome builds
    Author: Mamana Mbiyavanga
    Version: 1.0.0
========================================================================================
*/

nextflow.enable.dsl = 2

/*
========================================================================================
    PARAMETER VALIDATION
========================================================================================
*/

def helpMessage() {
    log.info"""
    =========================================
     vcf-liftover v${workflow.manifest.version}
    =========================================
    
    Usage:
    nextflow run main.nf [options]
    
    Required parameters:
      --input                 Input can be:
                              • Single VCF file: sample.vcf.gz
                              • Multiple VCF files: "*.vcf.gz" or file1.vcf.gz,file2.vcf.gz
                              • CSV file: samples.csv (with sample_id,vcf_path columns)
      --chain_file           Chain file for liftover (e.g., hg19ToHg38.over.chain.gz)
      --target_fasta         Target reference genome FASTA file
    
    Optional parameters:
      --source_build         Source genome build [default: hg19]
      --target_build         Target genome build [default: hg38]
      --chr_mapping          Chromosome mapping file for renaming
                              (auto-generated if not provided, e.g., 4→chr4 for hg19→hg38)
      --outdir               Output directory [default: ./results]
      --split_by_chr         Split processing by chromosome [default: false]
      --validate_output      Validate output VCF files [default: true]
    
    Resource parameters:
      --max_memory           Maximum memory [default: 128.GB]
      --max_cpus             Maximum CPUs [default: 16]
      --max_time             Maximum time [default: 240.h]
    
    Container parameters:
      --singularity_cache_dir Singularity cache directory [default: ~/.singularity]
      --scratch_dir          Scratch directory [default: /tmp]
    
    Profiles:
      -profile singularity   Use Singularity containers
      -profile slurm         Use SLURM executor
      -profile test          Use test data
      -profile docker        Use Docker containers
    
    Examples:
      # Single VCF file (use absolute path)
      nextflow run main.nf -profile singularity \\
        --input /absolute/path/to/sample.vcf.gz \\
        --chain_file chains/hg19ToHg38.over.chain.gz \\
        --target_fasta hg38.fa

      # Multiple VCF files (wildcard - IMPORTANT: use quotes and absolute path)
      nextflow run main.nf -profile singularity \\
        --input "/absolute/path/to/*.vcf.gz" \\
        --chain_file chains/hg19ToHg38.over.chain.gz \\
        --target_fasta hg38.fa

      # Multiple VCF files (comma-separated with absolute paths)
      nextflow run main.nf -profile singularity \\
        --input "/path/file1.vcf.gz,/path/file2.vcf.gz,/path/file3.vcf.gz" \\
        --chain_file chains/hg19ToHg38.over.chain.gz \\
        --target_fasta hg38.fa

      # CSV file with chromosome renaming
      nextflow run main.nf -profile singularity,slurm \\
        --input samples.csv \\
        --chain_file chains/hg19ToHg38.over.chain.gz \\
        --target_fasta hg38.fa \\
        --chr_mapping chr_mapping.txt

      # Test run
      nextflow run main.nf -profile test,singularity

    IMPORTANT NOTES:
      • Always use ABSOLUTE PATHS for input files when running from different directories
      • For wildcard patterns, ALWAYS use QUOTES: --input "/absolute/path/*.vcf.gz"
      • Without quotes, your shell will expand the wildcard and only pass the first file
    """.stripIndent()
}

// Function to check if input is VCF file
def isVcfFile(input) {
    return input.toString().toLowerCase().endsWith('.vcf') ||
           input.toString().toLowerCase().endsWith('.vcf.gz') ||
           input.toString().toLowerCase().endsWith('.bcf')
}

// Function to check if input is CSV file
def isCsvFile(input) {
    return input.toString().toLowerCase().endsWith('.csv')
}

// Function to create channel from input parameter
def createInputChannel(input_param) {
    if (isCsvFile(input_param)) {
        // CSV file input
        return Channel
            .fromPath(input_param, checkIfExists: true)
            .splitCsv(header: true)
            .map { row -> [row.sample_id, file(row.vcf_path)] }
    } else if (input_param.contains(',')) {
        // Comma-separated VCF files
        return Channel
            .fromList(input_param.split(','))
            .map { vcf_path ->
                def vcf_file = file(vcf_path.trim())
                def sample_id = vcf_file.baseName.replaceAll(/\.vcf(\.gz)?$/, '')
                [sample_id, vcf_file]
            }
    } else if (input_param.contains('*') || input_param.contains('?')) {
        // Wildcard pattern
        return Channel
            .fromPath(input_param, checkIfExists: true)
            .map { vcf_file ->
                def sample_id = vcf_file.baseName.replaceAll(/\.vcf(\.gz)?$/, '')
                [sample_id, vcf_file]
            }
    } else {
        // Single VCF file
        def vcf_file = file(input_param)
        def sample_id = vcf_file.baseName.replaceAll(/\.vcf(\.gz)?$/, '')
        return Channel.of([sample_id, vcf_file])
    }
}

// Function to validate input files before workflow execution
def validateInputFiles(input_param) {
    def launchDir = workflow.launchDir
    def errors = []

    if (isCsvFile(input_param)) {
        // Validate CSV file exists
        def csv_file = file(input_param)
        if (!csv_file.exists()) {
            return formatFileNotFoundError(input_param, "CSV file", launchDir)
        }

        // Validate VCF files listed in CSV
        def csv_errors = []
        csv_file.splitCsv(header: true).each { row ->
            if (row.vcf_path) {
                def vcf_file = file(row.vcf_path)
                if (!vcf_file.exists()) {
                    csv_errors << "  - ${row.sample_id ?: 'unknown'}: ${row.vcf_path}"
                }
            }
        }

        if (csv_errors) {
            errors << "ERROR: The following VCF files listed in the CSV do not exist:\n${csv_errors.join('\n')}"
            errors << "\nCurrent directory: ${launchDir}"
            errors << "\nSuggestions:"
            errors << "  • Ensure VCF paths in the CSV are correct"
            errors << "  • Use absolute paths in the CSV file"
            errors << "  • If using relative paths, they should be relative to: ${launchDir}"
            return errors.join('\n')
        }
    } else if (input_param.contains(',')) {
        // Validate comma-separated VCF files
        def missing_files = []
        input_param.split(',').each { vcf_path ->
            def vcf_file = file(vcf_path.trim())
            if (!vcf_file.exists()) {
                missing_files << "  - ${vcf_path.trim()}"
            }
        }

        if (missing_files) {
            errors << "ERROR: The following VCF files do not exist:\n${missing_files.join('\n')}"
            errors << "\nCurrent directory: ${launchDir}"
            errors << "\nSuggestions:"
            errors << "  • Check if the file paths are correct"
            errors << "  • Use absolute paths: /full/path/to/file.vcf.gz"
            errors << "  • If using relative paths, they should be relative to: ${launchDir}"
            return errors.join('\n')
        }
    } else if (input_param.contains('*') || input_param.contains('?')) {
        // Validate wildcard pattern matches files
        def matched_files = file(input_param)
        if (!matched_files || (matched_files instanceof List && matched_files.isEmpty())) {
            errors << "ERROR: No files found matching pattern: ${input_param}"
            errors << "\nCurrent directory: ${launchDir}"
            errors << "\nSuggestions:"
            errors << "  • Check if the wildcard pattern is correct"
            errors << "  • Verify files exist: ls -la ${input_param}"
            errors << "  • The pattern is evaluated relative to: ${launchDir}"
            return errors.join('\n')
        }
    } else {
        // Validate single VCF file
        def vcf_file = file(input_param)
        if (!vcf_file.exists()) {
            return formatFileNotFoundError(input_param, "VCF file", launchDir)
        }
    }

    return null  // No errors
}

// Helper function to format file not found error message
def formatFileNotFoundError(filepath, filetype, launchDir) {
    def errors = []
    errors << "ERROR: ${filetype} not found: ${filepath}"
    errors << "\nCurrent directory: ${launchDir}"
    errors << "\nSuggestions:"
    errors << "  • Check if the file path is correct"
    errors << "  • Use an absolute path: /full/path/to/file"
    errors << "  • If using a relative path, ensure it's relative to: ${launchDir}"
    errors << "  • Verify the file exists: ls -la ${filepath}"
    return errors.join('\n')
}

/*
========================================================================================
    IMPORT MODULES AND WORKFLOWS
========================================================================================
*/

include { LIFTOVER_WORKFLOW } from './workflows/liftover'

/*
========================================================================================
    MAIN WORKFLOW
========================================================================================
*/

workflow {

    // Show help message if requested
    if (params.help) {
        helpMessage()
        exit 0
    }

    // Validate required parameters
    if (!params.input) {
        log.error "ERROR: --input parameter is required"
        helpMessage()
        exit 1
    }
    if (!params.chain_file) {
        log.error "ERROR: --chain_file parameter is required"
        helpMessage()
        exit 1
    }
    if (!params.target_fasta) {
        log.error "ERROR: --target_fasta parameter is required"
        helpMessage()
        exit 1
    }

    // Validate input files exist before starting workflow
    def validation_error = validateInputFiles(params.input)
    if (validation_error) {
        log.error "\n${validation_error}\n"
        exit 1
    }

    // Validate chain file exists
    def chain_file_obj = file(params.chain_file)
    if (!chain_file_obj.exists()) {
        log.error formatFileNotFoundError(params.chain_file, "Chain file", workflow.launchDir)
        exit 1
    }

    // Validate target FASTA exists
    def target_fasta_obj = file(params.target_fasta)
    if (!target_fasta_obj.exists()) {
        log.error formatFileNotFoundError(params.target_fasta, "Target FASTA file", workflow.launchDir)
        exit 1
    }

    log.info """
    =========================================
     vcf-liftover v${workflow.manifest.version}
    =========================================
    Input           : ${params.input}
    Chain file      : ${params.chain_file}
    Target FASTA    : ${params.target_fasta}
    Source build    : ${params.source_build}
    Target build    : ${params.target_build}
    Chr mapping     : ${params.chr_mapping ?: 'None'}
    Output dir      : ${params.outdir}
    Split by chr    : ${params.split_by_chr}
    Validate output : ${params.validate_output}
    =========================================
    """.stripIndent()

    // Input channels are already created above

    // Prepare reference files
    chain_file = file(params.chain_file)
    target_fasta = file(params.target_fasta)
    chr_mapping = params.chr_mapping ? file(params.chr_mapping) : []

    // Run main liftover workflow
    LIFTOVER_WORKFLOW(
        params.input,
        chain_file,
        target_fasta,
        chr_mapping
    )
}

/*
========================================================================================
    WORKFLOW COMPLETION
========================================================================================
*/

workflow.onComplete {
    log.info """
    =========================================
     Pipeline completed!
    =========================================
    Completed at : ${workflow.complete}
    Duration     : ${workflow.duration}
    Success      : ${workflow.success}
    Work dir     : ${workflow.workDir}
    Exit status  : ${workflow.exitStatus}
    Error report : ${workflow.errorReport ?: 'None'}
    =========================================
    """.stripIndent()
    
    if (workflow.success) {
        log.info "Pipeline completed successfully!"
        log.info "Results are in: ${params.outdir}"
    } else {
        log.error "Pipeline failed!"
        log.error "Check the error report above for details"
    }
}

import groovy.json.JsonOutput

// Emit a structured error descriptor under `${params.logs}/fedimpute_error.json`
// (see docs/PIPELINE_ERROR_SCHEMA.md in the fedimpute repo). The FedImpute
// backend reads this file via the WES outputs endpoint and renders a typed
// error UI with a remediation button; if the file is absent the backend
// falls back to parsing stdout.
def emitStructuredError(Map err) {
    try {
        // Prefer params.logs (checkref-style), then params.outdir/logs, then launchDir/logs
        def logsPath
        if (params.containsKey('logs') && params.logs) {
            logsPath = "${params.logs}"
        } else if (params.containsKey('outdir') && params.outdir) {
            logsPath = "${params.outdir}/logs"
        } else {
            logsPath = "${workflow.launchDir}/logs"
        }
        def logsDir = file(logsPath)
        logsDir.mkdirs()
        def payload = [version: "1"] + err
        file("${logsPath}/fedimpute_error.json").text =
            JsonOutput.prettyPrint(JsonOutput.toJson(payload))
    } catch (Exception e) {
        log.warn "Failed to write fedimpute_error.json: ${e.message}"
    }
}

workflow.onError {
    log.error "Pipeline failed with error: ${workflow.errorMessage}"

    // Best-effort classification of the failure so the FedImpute UI can
    // surface a meaningful code + remediation instead of a bare
    // "EXECUTOR_ERROR". We look at the workflow error message text and,
    // where the pattern is unambiguous, assign a specific code.
    def msg = (workflow.errorMessage ?: '').toString()
    def code = 'PIPELINE_FAILED'
    def severity = 'pipeline_error'
    def remediation = null
    def summary = "vcf-liftover pipeline failed"

    if (msg =~ /(?i)GENERATE_CHR_MAPPING.*exit status \(1\)/ ||
        msg =~ /(?i)Could not extract chromosomes/) {
        code = 'CHR_EXTRACTION_FAILED'
        severity = 'user_error'
        summary = "Could not extract chromosomes from the input VCF. The file may be truncated, missing an index, or in an unsupported format."
        remediation = [
            kind: 'retry',
            hint: 'Verify the VCF opens with `bcftools view` locally, and that it has a .tbi or .csi index if gzipped. Then re-upload.',
        ]
    } else if (msg =~ /(?i)LIFTOVER.*exit status \(1\)/) {
        code = 'LIFTOVER_FAILED'
        severity = 'user_error'
        summary = "Liftover process failed. This usually means the source build does not match the chain file."
        remediation = [
            kind: 'select_panel',
            hint: 'Check that the source and target builds correspond to the selected chain file (e.g. hg19 -> hg38 needs hg19ToHg38.over.chain).',
        ]
    } else if (msg =~ /(?i)chain.*not found|target_fasta.*not found/) {
        code = 'MISSING_REFERENCE_FILE'
        severity = 'pipeline_error'
        summary = "A required reference file (chain or target FASTA) is missing from the workflow configuration."
        remediation = [
            kind: 'contact_support',
            hint: 'This is a service-side configuration issue; the operator needs to fix the workflow configuration.',
        ]
    }

    emitStructuredError([
        code: code,
        severity: severity,
        summary: summary,
        detail: msg.take(2000),
        remediation: remediation,
    ])
}
