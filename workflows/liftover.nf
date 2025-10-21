/*
========================================================================================
    Main Liftover Workflow
========================================================================================
    Orchestrates the complete VCF liftover process
========================================================================================
*/

// Import all required modules
include { INPUT_HANDLER } from '../modules/input_handler'
include { INPUT_CHECK } from '../modules/input_check'
include { VALIDATE_CHROMOSOMES } from '../modules/validate_chromosomes'
include { CROSSMAP_VCF } from '../modules/crossmap'
include { SORT_VCF } from '../modules/sort_vcf'
include { GENERATE_CHR_MAPPING } from '../modules/generate_chr_mapping'
include { RENAME_CHROMOSOMES } from '../modules/rename_chromosomes'
include { FIX_CONTIG_HEADER } from '../modules/fix_contig'
include { INDEX_VCF } from '../modules/index_vcf'
include { VALIDATE_VCF } from '../modules/validate_vcf'
include { LIFTOVER_STATS } from '../modules/liftover_stats'

workflow LIFTOVER_WORKFLOW {
    take:
    input_param   // String: input parameter (VCF file(s) or CSV)
    chain_file    // Path: chain file
    target_fasta  // Path: target reference
    chr_mapping   // Path: chromosome mapping (optional)

    main:
    // Process input to get standardized CSV
    script_file = file("${projectDir}/bin/process_input.py")
    INPUT_HANDLER(input_param, workflow.launchDir, script_file)

    // Parse CSV to get VCF files
    validated_csv = INPUT_CHECK(INPUT_HANDLER.out.csv)

    // Validate chromosome compatibility before running liftover
    target_fasta_fai = file("${target_fasta}.fai")
    VALIDATE_CHROMOSOMES(validated_csv, target_fasta, target_fasta_fai)

    log.info """
    ========================================
     Starting Liftover Workflow
    ========================================
    Chain file: ${chain_file}
    Target FASTA: ${target_fasta}
    Chr mapping: ${chr_mapping ?: 'None'}
    ========================================
    """.stripIndent()

    // Convert CSV to channel of tuples
    vcf_files = VALIDATE_CHROMOSOMES.out.csv
        .splitCsv(header: true)
        .map { row -> [row.sample_id, file(row.vcf_path)] }

    // Combine inputs for CrossMap
    crossmap_input = vcf_files.map { sample_id, vcf ->
        [sample_id, vcf, chain_file, target_fasta]
    }

    // Step 1: Run CrossMap liftover
    log.info "Step 1: Running CrossMap liftover..."
    CROSSMAP_VCF(crossmap_input)

    // Step 2: Sort VCF files
    log.info "Step 2: Sorting VCF files..."
    SORT_VCF(CROSSMAP_VCF.out.vcf)

    // Step 3: Generate or use chromosome mapping
    if (chr_mapping && !chr_mapping.isEmpty()) {
        // User provided a custom mapping file
        log.info "Step 3: Using user-provided chromosome mapping..."

        // Create channel with mapping for each sample
        sorted_with_mapping = SORT_VCF.out.vcf.map { sample_id, vcf ->
            [sample_id, vcf, chr_mapping]
        }
    } else {
        // Auto-generate chromosome mapping based on VCF and reference
        log.info "Step 3: Auto-generating chromosome mapping..."
        GENERATE_CHR_MAPPING(SORT_VCF.out.vcf, target_fasta_fai)

        // Combine sorted VCF with generated mapping
        sorted_with_mapping = SORT_VCF.out.vcf.join(
            GENERATE_CHR_MAPPING.out.mapping
        ).map { sample_id, vcf, mapping ->
            [sample_id, vcf, mapping]
        }
    }

    // Step 4: Rename chromosomes using mapping (always performed now)
    log.info "Step 4: Renaming chromosomes..."
    RENAME_CHROMOSOMES(sorted_with_mapping)
    sorted_vcf = RENAME_CHROMOSOMES.out.vcf

    // Step 5: Fix contig headers
    log.info "Step 5: Fixing contig headers..."
    FIX_CONTIG_HEADER(sorted_vcf, target_fasta)

    // Step 6: Index final VCF files
    log.info "Step 6: Indexing VCF files..."
    INDEX_VCF(FIX_CONTIG_HEADER.out.vcf)

    // Step 7: Validate output if requested
    if (params.validate_output) {
        log.info "Step 7: Validating output VCF files..."
        VALIDATE_VCF(INDEX_VCF.out.vcf_with_index)
        validation_reports = VALIDATE_VCF.out.report
    } else {
        log.info "Step 7: Skipping validation (validate_output = false)"
        validation_reports = Channel.empty()
    }

    // Step 8: Generate comprehensive statistics
    log.info "Step 8: Generating liftover statistics..."
    LIFTOVER_STATS(
        CROSSMAP_VCF.out.log.collect(),
        INDEX_VCF.out.vcf_with_index.map { _sample_id, vcf, _index -> vcf }.collect()
    )

    emit:
    // Final outputs
    vcf = INDEX_VCF.out.vcf_with_index
    stats = LIFTOVER_STATS.out.report
    logs = CROSSMAP_VCF.out.log
    unmap = CROSSMAP_VCF.out.unmap
    validation = validation_reports
    summary_csv = LIFTOVER_STATS.out.csv
    summary_stats = LIFTOVER_STATS.out.stats
}
