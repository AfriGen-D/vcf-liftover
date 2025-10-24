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
include { CHECK_BUILD_MISMATCH } from '../modules/check_build_mismatch'
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

    // Step 0: Check genome build compatibility (OPTIONAL - can be disabled)
    if (params.check_build_compatibility != false) {
        log.info "Step 0: Checking genome build compatibility..."
        CHECK_BUILD_MISMATCH(vcf_files, chain_file, target_fasta)

        // Check for build mismatch markers
        CHECK_BUILD_MISMATCH.out.marker
            .collect()
            .subscribe { markers ->
                if (markers.size() > 0) {
                    log.error """
╔════════════════════════════════════════════════════════════════════════════╗
║                     WORKFLOW TERMINATED GRACEFULLY                         ║
║                        Build Mismatch Detected                             ║
╚════════════════════════════════════════════════════════════════════════════╝

The pipeline detected that your VCF file(s) and chain file use incompatible
genome builds. Proceeding would produce INCORRECT RESULTS.

Build mismatch detected in ${markers.size()} sample(s).

Check the build compatibility reports in:
  ${params.outdir}/build_reports/

Solutions:
  • Verify your VCF genome build matches the chain file source build
  • Use the correct chain file for your data
  • Convert your VCF to the expected build first

Common Examples:
  • If VCF is hg38 but you want hg19: Use hg38ToHg19.over.chain.gz
  • If VCF is hg19 and you want hg38: Use hg19ToHg38.over.chain.gz
  • If VCF is already at target build: No liftover needed!

To bypass this check (NOT RECOMMENDED):
  nextflow run main.nf --check_build_compatibility false ...
"""
                    // Gracefully exit (not error code, just stop)
                    System.exit(0)
                }
            }

        // Filter out failed samples based on build check status
        build_check_status = CHECK_BUILD_MISMATCH.out.status
            .map { sample_id, check_type, status_file ->
                def status = status_file.text.trim()
                [sample_id, status]
            }

        // Only proceed with samples that passed build check
        vcf_files_filtered = vcf_files
            .join(build_check_status)
            .filter { sample_id, vcf, status -> status == 'PASSED' }
            .map { sample_id, vcf, status -> [sample_id, vcf] }

        // Log filtered samples
        vcf_files_filtered.count().subscribe { count ->
            if (count == 0) {
                log.error "All samples failed build compatibility check. Cannot proceed."
                System.exit(1)
            } else {
                log.info "Build compatibility check: ${count} sample(s) passed"
            }
        }

        vcf_files_for_liftover = vcf_files_filtered
    } else {
        log.warn "Build compatibility check DISABLED - proceeding without validation"
        log.warn "WARNING: This may produce incorrect results if builds don't match!"
        vcf_files_for_liftover = vcf_files
    }

    // Combine inputs for CrossMap
    crossmap_input = vcf_files_for_liftover.map { sample_id, vcf ->
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
