/*
========================================================================================
    Count Lifted Variants
========================================================================================
    Appends lifted / rejected / swapped variant counts to the Picard log.
    Lives in the vcf_processing container because it needs bcftools, which
    the picard container doesn't carry.
========================================================================================
*/

process COUNT_LIFTED_VARIANTS {
    tag "${sample_id}"
    label 'vcf_processing'

    // Publish the picard log so downstream consumers (the FedImpute QC card,
    // human inspection) can read the lifted/rejected/swapped counts directly
    // without trawling the Nextflow work dir. Before this, the log stayed
    // inside the per-task workdir under `work/<hash>/<sample>.picard.log`
    // and nothing outside the workflow could see the real counts. The
    // 2026-05-12 LIFTOVER_STATS-writes-zeros bug was rooted partly in this:
    // the stats Python script only knew CrossMap-format log shape (which
    // doesn't appear under the Picard pathway), so even though
    // `Lifted variants: N` lines existed in the workdir, no published
    // artifact carried them.
    publishDir "${params.outdir}/picard_logs", mode: 'copy', pattern: '*.picard.log'

    input:
    tuple val(sample_id), path(lifted_vcf), path(rejected_vcf), path(picard_log_in)

    output:
    tuple val(sample_id), path("${sample_id}.picard.log"), emit: log

    script:
    """
    cp ${picard_log_in} ${sample_id}.picard.log
    lifted_count=\$(bcftools view -H ${lifted_vcf} | wc -l)
    rejected_count=\$(bcftools view -H ${rejected_vcf} | wc -l)
    swapped_count=\$(bcftools view -H ${lifted_vcf} | grep -c 'SwappedAlleles' || true)
    {
      echo "Lifted variants: \$lifted_count"
      echo "Rejected variants: \$rejected_count"
      echo "REF/ALT swapped variants: \$swapped_count"
    } >> ${sample_id}.picard.log
    """
}
