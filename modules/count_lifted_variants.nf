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
