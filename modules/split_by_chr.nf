/*
========================================================================================
    Split-by-Chromosome Process
========================================================================================
    Splits a single multi-chromosome VCF into one file per chromosome present
    in the input. Downstream consumers (notably imputationserver2) require
    one VCF per chromosome; without this step, users have to manually split
    a liftover output before submitting to imputation.

    Only chromosomes that actually have variants are emitted (we read the
    tabix index stats rather than enumerating chr1..chr22+X+Y+MT) so the
    output set matches what's in the file.
========================================================================================
*/

process SPLIT_BY_CHR {
    tag "${sample_id}"
    label 'vcf_processing'

    publishDir "${params.outdir}/per_chromosome", mode: 'copy'

    input:
    tuple val(sample_id), path(vcf), path(tbi)

    output:
    tuple val(sample_id), path("*.chr*.vcf.gz"), path("*.chr*.vcf.gz.tbi"), emit: split_vcfs
    path("${sample_id}.split_summary.txt"), emit: summary

    script:
    // Strip .vcf.gz from the input so per-chr outputs are named
    // <basename>.<chr>.vcf.gz rather than <basename>.vcf.gz.<chr>.vcf.gz.
    def base = vcf.name.replaceAll(/\.vcf\.gz$/, '')
    """
    set -euo pipefail

    # Enumerate chromosomes that actually have records. tabix's --stats
    # output is: <seqname>\\t<#records>\\t... -- we keep seqnames whose
    # record count is non-zero.
    tabix --list-chroms ${vcf} > all_chroms.txt
    : > chroms_with_data.txt
    while read chr; do
        # bcftools index --stats returns per-seq record counts; filter empty
        n=\$(bcftools index --stats ${vcf} | awk -v c="\$chr" -F'\\t' '\$1==c {print \$3; exit}')
        if [ -n "\$n" ] && [ "\$n" != "0" ]; then
            echo "\$chr" >> chroms_with_data.txt
        fi
    done < all_chroms.txt

    if [ ! -s chroms_with_data.txt ]; then
        echo "ERROR: No chromosomes with variants found in ${vcf}" >&2
        exit 1
    fi

    # Split. Use bcftools view -r (region) which is cheap when the file is
    # indexed (it is -- we receive the .tbi alongside).
    : > "${sample_id}.split_summary.txt"
    echo "Per-chromosome split of ${vcf}" >> "${sample_id}.split_summary.txt"
    echo "==========================================" >> "${sample_id}.split_summary.txt"
    while read chr; do
        out="${base}.\${chr}.vcf.gz"
        bcftools view -r "\${chr}" -Oz -o "\${out}" ${vcf}
        tabix -f -p vcf "\${out}"
        n_records=\$(bcftools view -H "\${out}" | wc -l)
        size=\$(du -h "\${out}" | cut -f1)
        printf "%-8s %12s records  %s\\n" "\${chr}" "\${n_records}" "\${size}" \
            >> "${sample_id}.split_summary.txt"
    done < chroms_with_data.txt

    echo "Split complete: \$(wc -l < chroms_with_data.txt) chromosomes" \
        >> "${sample_id}.split_summary.txt"
    """
}
