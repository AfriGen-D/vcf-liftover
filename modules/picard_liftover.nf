/*
========================================================================================
    Picard LiftoverVcf Process
========================================================================================
    Performs coordinate liftover using Picard LiftoverVcf.
    Unlike CrossMap, Picard correctly handles REF/ALT swaps when the reference
    allele changes between genome builds (--RECOVER_SWAPPED_REF_ALT true).

    Container requirements: picard + java only. Input VCF must be .vcf.gz
    (BCF→VCF prep happens upstream in PREPARE_VCF_FOR_PICARD). Variant
    counts happen downstream in COUNT_LIFTED_VARIANTS so the bcftools
    calls live in a container that actually has bcftools.
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
    tuple val(sample_id), path("${sample_id}.picard.log"), emit: log

    script:
    def java_mem = task.memory ? "-Xmx${Math.max(task.memory.toGiga() - 1, 1)}g" : "-Xmx2g"
    """
    set -o pipefail

    echo "Starting Picard LiftoverVcf for sample: ${sample_id}"
    echo "Input VCF: ${vcf}"
    echo "Chain file: ${chain_file}"
    echo "Target FASTA: ${target_fasta}"

    # snappy.disable: mamana/picard:3.3.0 lacks libsnappy native binary, so
    # the spill-to-disk path in SortingCollection crashes once MAX_RECORDS_IN_RAM
    # is exceeded. Falling back to GZIP for temp streams is fine.
    # WARN_ON_MISSING_CONTIG=true: Picard's default is to FAIL the whole run
    # if a chain-mapped contig is absent from the target FASTA. The hg38
    # reference deployed on NFS (`/mnt/impute-storage/apps/references/
    # human/GRCh38/hg38.fasta`) is primary-only -- it omits the 100+ alt
    # haplotypes (`chrN_*_alt`) that the hg19ToHg38 chain knows how to map
    # to. Without this flag, any input variant that lands on an alt contig
    # crashes the whole pipeline; with it, those variants are written to
    # the rejected-VCF with a clear "missing contig" reason and the run
    # proceeds. 2026-05-12 prod regression: a job submitted by Jacqui
    # with Sch_phased.fixed.sorted.vcf.gz failed at
    # `chr7_KI270803v1_alt` after lifting 1.4M variants successfully.
    _JAVA_OPTIONS="${java_mem} -Dsamjdk.snappy.disable=true" picard LiftoverVcf \\
        -I ${vcf} \\
        -O ${sample_id}.lifted.vcf.gz \\
        -C ${chain_file} \\
        -R ${target_fasta} \\
        --REJECT ${sample_id}.rejected.vcf.gz \\
        --RECOVER_SWAPPED_REF_ALT true \\
        --WRITE_ORIGINAL_POSITION true \\
        --WRITE_ORIGINAL_ALLELES true \\
        --WARN_ON_MISSING_CONTIG true \\
        --VALIDATION_STRINGENCY LENIENT \\
        --MAX_RECORDS_IN_RAM 100000 \\
        2>&1 | tee ${sample_id}.picard.log

    echo "Picard LiftoverVcf completed for sample: ${sample_id}"
    """
}
