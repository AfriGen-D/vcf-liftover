/*
========================================================================================
    Build Compatibility Validation Process
========================================================================================
    Checks if VCF genome build matches the expected build for the chain file.
    Prevents incorrect liftover results from build mismatches.

    Example Problem:
        VCF: hg38 (already at target build)
        Chain: hg19ToHg38.over.chain.gz (expects hg19 input!)
        Result: INCOMPATIBLE - will produce wrong coordinates
========================================================================================
*/

process CHECK_BUILD_MISMATCH {
    tag "${sample_id}"
    label 'general'

    // Don't fail workflow immediately - let us handle gracefully
    errorStrategy 'ignore'

    publishDir "${params.outdir}/build_reports", mode: 'copy'

    input:
    tuple val(sample_id), path(vcf)
    path chain_file
    path target_fasta

    output:
    path "BUILD_MISMATCH_DETECTED_${sample_id}", optional: true, emit: marker
    path "${sample_id}_build_compatibility.txt", emit: report
    tuple val(sample_id), val('build_check'), path("${sample_id}_build_status.txt"), emit: status

    script:
    """
    echo "Checking genome build compatibility for sample: ${sample_id}"
    echo "VCF: ${vcf}"
    echo "Chain: ${chain_file}"
    echo "Target: ${target_fasta}"

    # Run build compatibility check
    check_build_compatibility.py \\
        --vcf ${vcf} \\
        --chain ${chain_file} \\
        --target-ref ${target_fasta} \\
        --sample-id ${sample_id} \\
        --output ${sample_id}_build_compatibility.txt

    # Check exit status
    if [ \$? -eq 0 ]; then
        echo "PASSED" > ${sample_id}_build_status.txt
        echo "✓ Build compatibility check passed for ${sample_id}"
    else
        echo "FAILED" > ${sample_id}_build_status.txt
        # Create marker file if mismatch detected
        if [ -f "BUILD_MISMATCH_DETECTED" ]; then
            mv BUILD_MISMATCH_DETECTED BUILD_MISMATCH_DETECTED_${sample_id}
            echo "❌ Build mismatch detected for ${sample_id}"
        fi
    fi
    """
}
