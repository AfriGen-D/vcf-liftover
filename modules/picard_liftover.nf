/*
========================================================================================
    Picard LiftoverVcf Process
========================================================================================
    Performs coordinate liftover using GATK/Picard LiftoverVcf.
    Unlike CrossMap, Picard correctly handles REF/ALT swaps when the reference
    allele changes between genome builds (--RECOVER_SWAPPED_REF_ALT true).
========================================================================================
*/

process PICARD_LIFTOVER {
    tag "${sample_id}"
    label 'picard'

    input:
    tuple val(sample_id), path(vcf), path(chain_file), path(target_fasta), path(target_fasta_fai), path(target_fasta_dict)

    output:
    tuple val(sample_id), path("${sample_id}.lifted.vcf.gz"), emit: vcf
    tuple val(sample_id), path("${sample_id}.rejected.vcf.gz"), emit: rejected
    path("${sample_id}.picard.log"), emit: log

    script:
    def java_mem = task.memory ? "-Xmx${Math.max(task.memory.toGiga() - 1, 1)}g" : "-Xmx2g"
    """
    echo "Starting Picard LiftoverVcf for sample: ${sample_id}"
    echo "Input VCF: ${vcf}"
    echo "Chain file: ${chain_file}"
    echo "Target FASTA: ${target_fasta}"

    # Convert BCF to VCF.gz if needed (Picard/HTSJDK cannot read BCF format)
    input_vcf="${vcf}"
    if [[ "${vcf}" == *.bcf ]]; then
        echo "Converting BCF to VCF.gz for Picard compatibility..."
        bcftools view -Oz -o ${sample_id}.input.vcf.gz ${vcf}
        bcftools index -t ${sample_id}.input.vcf.gz
        input_vcf="${sample_id}.input.vcf.gz"
    fi

    gatk --java-options "${java_mem}" LiftoverVcf \\
        -I \${input_vcf} \\
        -O ${sample_id}.lifted.vcf.gz \\
        -C ${chain_file} \\
        -R ${target_fasta} \\
        --REJECT ${sample_id}.rejected.vcf.gz \\
        --RECOVER_SWAPPED_REF_ALT true \\
        --WRITE_ORIGINAL_POSITION true \\
        --WRITE_ORIGINAL_ALLELES true \\
        --VALIDATION_STRINGENCY LENIENT \\
        --MAX_RECORDS_IN_RAM 100000 \\
        2>&1 | tee ${sample_id}.picard.log

    echo "Picard LiftoverVcf completed for sample: ${sample_id}"

    # Count variants in output and append to log
    lifted_count=\$(bcftools view -H ${sample_id}.lifted.vcf.gz 2>/dev/null | wc -l || echo "0")
    rejected_count=\$(bcftools view -H ${sample_id}.rejected.vcf.gz 2>/dev/null | wc -l || echo "0")
    swapped_count=\$(bcftools view -H ${sample_id}.lifted.vcf.gz 2>/dev/null | grep -c 'SwappedAlleles' || echo "0")

    echo "Lifted variants: \$lifted_count" | tee -a ${sample_id}.picard.log
    echo "Rejected variants: \$rejected_count" | tee -a ${sample_id}.picard.log
    echo "REF/ALT swapped variants: \$swapped_count" | tee -a ${sample_id}.picard.log
    """
}
