/*
========================================================================================
    Prepare VCF For Picard
========================================================================================
    Picard LiftoverVcf reads VCF/VCF.gz but not BCF. This process runs ahead
    of PICARD_LIFTOVER and converts BCF inputs to VCF.gz; for inputs that are
    already .vcf.gz it just symlinks the file under a uniform name. Lives in
    the vcf_processing container (has bcftools) so PICARD_LIFTOVER's container
    can stay bcftools-free.
========================================================================================
*/

process PREPARE_VCF_FOR_PICARD {
    tag "${sample_id}"
    label 'vcf_processing'

    input:
    tuple val(sample_id), path(vcf)

    output:
    tuple val(sample_id), path("${sample_id}.prep.vcf.gz"), emit: vcf

    script:
    """
    if [[ "${vcf}" == *.bcf ]]; then
        echo "Converting BCF to VCF.gz for Picard compatibility..."
        bcftools view -Oz -o ${sample_id}.prep.vcf.gz ${vcf}
        bcftools index -t ${sample_id}.prep.vcf.gz
    else
        ln -s \$(readlink -f ${vcf}) ${sample_id}.prep.vcf.gz
    fi
    """
}
