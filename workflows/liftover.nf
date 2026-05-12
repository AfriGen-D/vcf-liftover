/*
========================================================================================
    Main Liftover Workflow
========================================================================================
    Orchestrates the complete VCF liftover process.
    v2.0.0: Uses Picard LiftoverVcf (default) or CrossMap (legacy).
    Picard correctly handles REF/ALT swaps when the reference allele changes
    between genome builds.
========================================================================================
*/

// Import all required modules
include { INPUT_HANDLER } from '../modules/input_handler'
include { INPUT_CHECK } from '../modules/input_check'
include { VALIDATE_CHROMOSOMES } from '../modules/validate_chromosomes'
include { CHECK_BUILD_MISMATCH } from '../modules/check_build_mismatch'
include { CROSSMAP_VCF } from '../modules/crossmap'
include { FIX_MISMATCHED_REF } from '../modules/fix_mismatched_ref'
include { PREPARE_VCF_FOR_PICARD } from '../modules/prepare_vcf_for_picard'
include { PICARD_LIFTOVER } from '../modules/picard_liftover'
include { COUNT_LIFTED_VARIANTS } from '../modules/count_lifted_variants'
include { FILTER_REJECTED } from '../modules/filter_rejected'
include { SORT_VCF } from '../modules/sort_vcf'
include { GENERATE_CHR_MAPPING } from '../modules/generate_chr_mapping'
include { RENAME_CHROMOSOMES } from '../modules/rename_chromosomes'
include { FIX_CONTIG_HEADER } from '../modules/fix_contig'
include { INDEX_VCF } from '../modules/index_vcf'
include { VALIDATE_VCF } from '../modules/validate_vcf'
include { LIFTOVER_STATS } from '../modules/liftover_stats'
include { GENERATE_REPORT } from '../modules/generate_report'
include { SPLIT_BY_CHR } from '../modules/split_by_chr'

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

    // Reference files
    target_fasta_fai = file("${target_fasta}.fai")
    target_fasta_dict = file("${target_fasta}".replaceAll(/\.fasta$|\.fa$/, '.dict'))

    log.info """
    ========================================
     Starting Liftover Workflow
    ========================================
    Liftover tool: ${params.liftover_tool}
    Chain file: ${chain_file}
    Target FASTA: ${target_fasta}
    Chr mapping: ${chr_mapping ?: 'None'}
    ========================================
    """.stripIndent()

    // Convert CSV to channel of tuples
    vcf_files = validated_csv
        .splitCsv(header: true)
        .map { row -> [row.sample_id, file(row.vcf_path)] }

    // Step 0: Check genome build compatibility (OPTIONAL - can be disabled)
    if (params.check_build_compatibility != false) {
        log.info "Step 0: Checking genome build compatibility..."
        CHECK_BUILD_MISMATCH(vcf_files, chain_file, target_fasta)

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

To bypass this check (NOT RECOMMENDED):
  nextflow run main.nf --check_build_compatibility false ...
"""
                    System.exit(0)
                }
            }

        build_check_status = CHECK_BUILD_MISMATCH.out.status
            .map { sample_id, check_type, status_file ->
                def status = status_file.text.trim()
                [sample_id, status]
            }

        vcf_files_filtered = vcf_files
            .join(build_check_status)
            .filter { sample_id, vcf, status -> status == 'PASSED' }
            .map { sample_id, vcf, status -> [sample_id, vcf] }

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
        vcf_files_for_liftover = vcf_files
    }

    // =========================================================================
    // Optional: pre-flight bcftools +fixref to flip swappable MismatchedRefAllele
    // before liftover. Off by default — opt in with --fix_mismatched_ref true.
    // Requires --source_fasta (the SOURCE build's reference).
    // =========================================================================
    if (params.fix_mismatched_ref) {
        if (!params.source_fasta) {
            log.error "fix_mismatched_ref=true requires --source_fasta <SOURCE build fasta>"
            System.exit(1)
        }
        log.info "Running bcftools +fixref preflight (source=${params.source_fasta})..."
        source_fasta_ch = file(params.source_fasta)
        FIX_MISMATCHED_REF(vcf_files_for_liftover, source_fasta_ch)
        vcf_files_for_liftover = FIX_MISMATCHED_REF.out.vcf
    }

    // =========================================================================
    // Liftover tool selection: picard (default) or crossmap (legacy)
    // =========================================================================

    if (params.liftover_tool == 'picard') {
        // -----------------------------------------------------------------
        // PICARD LIFTOVER PATHWAY (v2.0.0 default)
        // -----------------------------------------------------------------
        // Picard requires chr-prefixed contigs matching the chain file,
        // so chromosome renaming must happen BEFORE liftover.
        // -----------------------------------------------------------------

        // Step 1: Generate or use chromosome mapping
        if (chr_mapping && !chr_mapping.isEmpty()) {
            log.info "Step 1: Using user-provided chromosome mapping..."
            vcf_with_mapping = vcf_files_for_liftover.map { sample_id, vcf ->
                [sample_id, vcf, chr_mapping]
            }
        } else {
            log.info "Step 1: Auto-generating chromosome mapping..."
            GENERATE_CHR_MAPPING(vcf_files_for_liftover, target_fasta_fai)
            vcf_with_mapping = vcf_files_for_liftover.join(
                GENERATE_CHR_MAPPING.out.mapping
            ).map { sample_id, vcf, mapping ->
                [sample_id, vcf, mapping]
            }
        }

        // Step 2: Rename chromosomes (before Picard liftover)
        log.info "Step 2: Renaming chromosomes..."
        RENAME_CHROMOSOMES(vcf_with_mapping)

        // Step 3a: Prepare VCF for Picard (BCF→VCF.gz if needed; passthrough otherwise)
        log.info "Step 3a: Preparing VCF for Picard..."
        PREPARE_VCF_FOR_PICARD(RENAME_CHROMOSOMES.out.vcf)

        // Step 3b: Run Picard LiftoverVcf
        log.info "Step 3b: Running Picard LiftoverVcf..."
        picard_input = PREPARE_VCF_FOR_PICARD.out.vcf.map { sample_id, vcf ->
            [sample_id, vcf, chain_file, target_fasta, target_fasta_fai, target_fasta_dict]
        }
        PICARD_LIFTOVER(picard_input)

        // Step 3c: Count lifted/rejected/swapped variants (bcftools, separate label)
        counts_input = PICARD_LIFTOVER.out.vcf
            .join(PICARD_LIFTOVER.out.rejected)
            .join(PICARD_LIFTOVER.out.log)
        COUNT_LIFTED_VARIANTS(counts_input)

        // Step 4: Analyze rejected variants
        log.info "Step 4: Analyzing rejected variants..."
        FILTER_REJECTED(PICARD_LIFTOVER.out.rejected)

        // Step 5: Sort lifted VCF
        log.info "Step 5: Sorting lifted VCF files..."
        SORT_VCF(PICARD_LIFTOVER.out.vcf)

        // Step 6: Fix contig headers
        log.info "Step 6: Fixing contig headers..."
        FIX_CONTIG_HEADER(SORT_VCF.out.vcf, target_fasta)

        liftover_logs = COUNT_LIFTED_VARIANTS.out.log.map { _id, log_file -> log_file }

    } else {
        // -----------------------------------------------------------------
        // CROSSMAP PATHWAY (legacy v1.0.0 behavior)
        // -----------------------------------------------------------------

        // Step 1: Run CrossMap liftover
        log.info "Step 1: Running CrossMap liftover..."
        crossmap_input = vcf_files_for_liftover.map { sample_id, vcf ->
            [sample_id, vcf, chain_file, target_fasta]
        }
        CROSSMAP_VCF(crossmap_input)

        // Step 2: Sort VCF files
        log.info "Step 2: Sorting VCF files..."
        SORT_VCF(CROSSMAP_VCF.out.vcf)

        // Step 3: Generate or use chromosome mapping
        if (chr_mapping && !chr_mapping.isEmpty()) {
            log.info "Step 3: Using user-provided chromosome mapping..."
            sorted_with_mapping = SORT_VCF.out.vcf.map { sample_id, vcf ->
                [sample_id, vcf, chr_mapping]
            }
        } else {
            log.info "Step 3: Auto-generating chromosome mapping..."
            GENERATE_CHR_MAPPING(SORT_VCF.out.vcf, target_fasta_fai)
            sorted_with_mapping = SORT_VCF.out.vcf.join(
                GENERATE_CHR_MAPPING.out.mapping
            ).map { sample_id, vcf, mapping ->
                [sample_id, vcf, mapping]
            }
        }

        // Step 4: Rename chromosomes
        log.info "Step 4: Renaming chromosomes..."
        RENAME_CHROMOSOMES(sorted_with_mapping)

        // Step 5: Fix contig headers
        log.info "Step 5: Fixing contig headers..."
        FIX_CONTIG_HEADER(RENAME_CHROMOSOMES.out.vcf, target_fasta)

        liftover_logs = CROSSMAP_VCF.out.log
    }

    // =========================================================================
    // Common final steps
    // =========================================================================

    // Step N-2: Index final VCF files
    log.info "Indexing VCF files..."
    INDEX_VCF(FIX_CONTIG_HEADER.out.vcf)

    // Step N-1a: Optional per-chromosome split. Downstream consumers like
    // imputationserver2 reject multi-chromosome VCFs ("The provided VCF file
    // contains more than one chromosome"); enabling this produces a ready-
    // to-submit per_chromosome/<basename>.<chr>.vcf.gz set alongside the
    // merged output.
    if (params.split_by_chr) {
        log.info "Splitting output by chromosome..."
        SPLIT_BY_CHR(INDEX_VCF.out.vcf_with_index)
        per_chromosome_vcfs = SPLIT_BY_CHR.out.split_vcfs
        per_chromosome_split_summary = SPLIT_BY_CHR.out.summary
    } else {
        per_chromosome_vcfs = Channel.empty()
        per_chromosome_split_summary = Channel.empty()
    }

    // Step N-1: Validate output if requested
    if (params.validate_output) {
        log.info "Validating output VCF files..."
        VALIDATE_VCF(INDEX_VCF.out.vcf_with_index)
        validation_reports = VALIDATE_VCF.out.report
    } else {
        validation_reports = Channel.empty()
    }

    // Step N: Generate comprehensive statistics
    log.info "Generating liftover statistics..."
    LIFTOVER_STATS(
        liftover_logs.collect(),
        INDEX_VCF.out.vcf_with_index.map { _sample_id, vcf, _index -> vcf }.collect()
    )

    // Step N+1: Generate HTML report (Picard pathway only)
    if (params.liftover_tool == 'picard') {
        log.info "Generating HTML report..."
        nf_config = file("${projectDir}/nextflow.config")
        GENERATE_REPORT(
            COUNT_LIFTED_VARIANTS.out.log.map { _id, log_file -> log_file }.collect(),
            FILTER_REJECTED.out.summary.map { _id, txt -> txt }.collect(),
            nf_config
        )
        html_report = GENERATE_REPORT.out.report
        pdf_report = GENERATE_REPORT.out.pdf
    } else {
        html_report = Channel.empty()
        pdf_report = Channel.empty()
    }

    emit:
    vcf = INDEX_VCF.out.vcf_with_index
    per_chromosome = per_chromosome_vcfs
    per_chromosome_split_summary = per_chromosome_split_summary
    stats = LIFTOVER_STATS.out.report
    logs = liftover_logs
    validation = validation_reports
    summary_csv = LIFTOVER_STATS.out.csv
    summary_stats = LIFTOVER_STATS.out.stats
    html = html_report
    pdf = pdf_report
}
