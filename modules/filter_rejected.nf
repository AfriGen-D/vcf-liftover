/*
========================================================================================
    Filter Rejected Variants Process
========================================================================================
    Analyzes and summarizes variants rejected during Picard LiftoverVcf
========================================================================================
*/

process FILTER_REJECTED {
    tag "${sample_id}"
    label 'vcf_processing'

    publishDir "${params.outdir}/rejected", mode: 'copy'

    input:
    tuple val(sample_id), path(rejected_vcf)

    output:
    tuple val(sample_id), path("${sample_id}.rejected_summary.txt"), emit: summary

    script:
    """
    set -o pipefail
    OUT=${sample_id}.rejected_summary.txt
    echo "=== Rejected Variants Summary: ${sample_id} ===" > \$OUT
    echo "" >> \$OUT

    total=\$(bcftools view -H ${rejected_vcf} | wc -l)
    echo "Total rejected variants: \$total" >> \$OUT

    if [ "\$total" -gt 0 ]; then
        snps=\$(bcftools view -H -v snps ${rejected_vcf} | wc -l)
        indels=\$(bcftools view -H -v indels ${rejected_vcf} | wc -l)
        echo "SNPs: \$snps" >> \$OUT
        echo "Indels: \$indels" >> \$OUT

        echo "" >> \$OUT
        echo "Rejection reasons:" >> \$OUT
        bcftools query -f '%FILTER\\n' ${rejected_vcf} | sort | uniq -c | sort -rn >> \$OUT

        # ---- Remediation hint for MismatchedRefAllele ----
        # If MismatchedRefAllele dominates rejections, the input VCF's REF
        # alleles likely don't match the source build's reference. Surface
        # the --fix_mismatched_ref option so users don't have to discover it.
        mismatched=\$(bcftools query -f '%FILTER\\n' ${rejected_vcf} | grep -c 'MismatchedRefAllele' || true)
        if [ "\$mismatched" -ge 100 ] && [ "\$total" -ge 100 ]; then
            pct=\$(awk -v m=\$mismatched -v t=\$total 'BEGIN{printf "%.1f", (m/t)*100}')
            mismatched_pct_int=\$(awk -v m=\$mismatched -v t=\$total 'BEGIN{printf "%d", (m/t)*100}')
            if [ "\$mismatched_pct_int" -ge 50 ]; then
                {
                    echo ""
                    echo "WARNING: High MismatchedRefAllele rate (\$mismatched of \$total rejections = \${pct}%)"
                    echo ""
                    echo "This usually means the input VCF's REF alleles do not match the source"
                    echo "build's reference fasta — often because the VCF was aligned to a different"
                    echo "build or different fasta variant (chr-prefix, primary-assembly, etc.)."
                    echo ""
                    echo "To attempt automatic remediation, re-run liftover with:"
                    echo ""
                    echo "  --fix_mismatched_ref true \\\\"
                    echo "  --source_fasta /path/to/<source_build>.fasta"
                    echo ""
                    echo "This runs 'bcftools +fixref -m flip -d' before liftover, which flips"
                    echo "REF/ALT where alleles are simply swapped on different strands and drops"
                    echo "variants that cannot be flipped. Note: this transforms data (genotypes"
                    echo "are flipped alongside REF/ALT), so verify results carefully."
                } >> \$OUT
            fi
        fi
    fi

    echo "" >> \$OUT
    echo "=== End Summary ===" >> \$OUT

    cat \$OUT
    """
}
