---
layout: home

hero:
  name: "VCF Liftover"
  text: "Genomic Coordinate Conversion Pipeline"
  tagline: "A robust, production-ready Nextflow pipeline for converting VCF files between genome builds using CrossMap • Developed by AfriGen-D"
  image:
    src: /logo.png
    alt: VCF Liftover
  actions:
    - theme: brand
      text: Get Started
      link: /guide/getting-started
    - theme: alt
      text: View on GitHub
      link: https://github.com/AfriGen-D/vcf-liftover

features:
  - icon: 🧬
    title: Precise Genome Build Conversion
    details: Seamlessly converts genomic coordinates between reference builds (hg19 ↔ hg38) with industry-leading accuracy using CrossMap.
  - icon: ⚡
    title: Production-Ready Nextflow
    details: Built with Nextflow DSL2 for scalable, reproducible workflows with automatic resource management and error handling.
  - icon: 📊
    title: High-Throughput Processing
    details: Process thousands of VCF files simultaneously with intelligent batching, CSV input support, and parallel execution.
  - icon: 🔬
    title: Comprehensive Quality Control
    details: Built-in validation, detailed statistics, success rate tracking, and comprehensive error reporting for reliable results.
  - icon: 🐳
    title: Container-Ready Deployment
    details: Full Docker/Singularity support with pre-built containers for reproducible execution across any computing environment.
  - icon: 📚
    title: Complete Documentation
    details: Extensive tutorials, examples, and reference materials with step-by-step guides for researchers and bioinformaticians.
---

## Quick Start ​

Get started with vcf-liftover in just a few commands:

```bash
# Clone the repository
git clone https://github.com/AfriGen-D/vcf-liftover.git
cd vcf-liftover

# Run with your data
nextflow run main.nf \
  --input your_file.vcf.gz \
  --target_fasta /path/to/GRCh38.fa \
  --outdir results \
  -profile singularity
```

## What vcf-liftover Does ​

This Nextflow pipeline provides:

- **Coordinate Conversion**: Lifts over genomic coordinates from hg19 to hg38 using CrossMap
- **Smart Processing**: Automatically handles VCF sorting, indexing, and chromosome renaming
- **Quality Assessment**: Comprehensive statistics and validation reports
- **Multi-File Support**: Process multiple VCF files simultaneously with CSV batch input

## Documentation ​

- [Tutorials](/tutorials/) - Step-by-step learning exercises
- [Documentation](/docs/) - Comprehensive reference material
- [Reference](/reference/) - Complete parameter and configuration reference
- [Examples](/examples/) - Ready-to-use configurations

## Requirements ​

- Nextflow ≥ 22.10.1
- Docker, Singularity, or Conda
- Target VCF files (bgzipped and indexed)
- Target reference genome FASTA file
- CrossMap chain file (automatically downloaded)

## Support ​

- [GitHub Issues](https://github.com/AfriGen-D/vcf-liftover/issues)
- [Helpdesk](https://helpdesk.afrigen-d.org)
- [AfriGen-D](https://afrigen-d.org)