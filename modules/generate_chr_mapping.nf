/*
========================================================================================
    Generate Chromosome Mapping Process
========================================================================================
    Auto-generates chromosome mapping based on VCF and reference naming conventions
========================================================================================
*/

process GENERATE_CHR_MAPPING {
    tag "${sample_id}"
    label 'vcf_processing'

    input:
    tuple val(sample_id), path(vcf)
    path target_fasta_fai

    output:
    tuple val(sample_id), path("${sample_id}.chr_mapping.txt"), emit: mapping

    script:
    """
    echo "Generating chromosome mapping for sample: ${sample_id}"
    echo "VCF: ${vcf}"
    echo "Reference index: ${target_fasta_fai}"

    # Extract VCF chromosomes using bcftools
    echo "Extracting chromosomes from VCF..."
    vcf_chroms=\$(bcftools query -f '%CHROM\\n' ${vcf} 2>/dev/null | sort -u)

    if [ -z "\$vcf_chroms" ]; then
        echo "ERROR: Could not extract chromosomes from VCF" >&2
        exit 1
    fi

    echo "VCF chromosomes: \$vcf_chroms"

    # Extract reference chromosomes from FAI
    echo "Extracting chromosomes from reference..."
    ref_chroms=\$(cut -f1 ${target_fasta_fai})

    # Detect naming conventions
    vcf_has_chr=\$(echo "\$vcf_chroms" | grep -q "^chr" && echo "yes" || echo "no")
    ref_has_chr=\$(echo "\$ref_chroms" | head -10 | grep -q "^chr" && echo "yes" || echo "no")

    echo "VCF naming: \$vcf_has_chr prefix, Reference naming: \$ref_has_chr prefix"

    # Generate mapping if naming conventions differ
    if [ "\$vcf_has_chr" != "\$ref_has_chr" ]; then
        echo "Naming conventions differ - generating chromosome mapping..."

        > ${sample_id}.chr_mapping.txt

        for vcf_chr in \$vcf_chroms; do
            # Normalize (remove chr prefix if present)
            normalized=\$(echo "\$vcf_chr" | sed 's/^chr//')

            # Find matching reference chromosome
            if [ "\$ref_has_chr" = "yes" ]; then
                ref_chr="chr\${normalized}"
            else
                ref_chr="\${normalized}"
            fi

            # Check if reference has this chromosome
            if echo "\$ref_chroms" | grep -q "^\${ref_chr}\$"; then
                if [ "\$vcf_chr" != "\$ref_chr" ]; then
                    echo "\${vcf_chr}\t\${ref_chr}" >> ${sample_id}.chr_mapping.txt
                    echo "  \${vcf_chr} → \${ref_chr}"
                fi
            fi
        done

        if [ ! -s ${sample_id}.chr_mapping.txt ]; then
            echo "# No chromosome renaming needed" > ${sample_id}.chr_mapping.txt
            echo "No renaming needed - same naming convention"
        fi
    else
        echo "# No chromosome renaming needed" > ${sample_id}.chr_mapping.txt
        echo "No renaming needed - both use same naming convention"
    fi

    echo ""
    echo "Chromosome mapping generated: ${sample_id}.chr_mapping.txt"
    echo "Mapping contents:"
    cat ${sample_id}.chr_mapping.txt
    """
}
