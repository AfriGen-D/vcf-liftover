# Getting Started

vcf-liftover is a Nextflow pipeline designed for converting VCF files between genome builds using CrossMap. This guide will help you get up and running with the pipeline.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Nextflow** (version 22.10.1 or later)
- **Container engine**: Singularity or Docker
- **Java** 11 or later (for Nextflow)
- **Target reference genome**: GRCh38 FASTA file
- **Chain file**: hg19ToHg38.over.chain.gz (automatically downloaded)

## Quick Installation

### 1. Install Nextflow

```bash
# Install Nextflow
curl -s https://get.nextflow.io | bash

# Make it executable and move to PATH
chmod +x nextflow
sudo mv nextflow /usr/local/bin/
```

### 2. Clone the Pipeline

```bash
git clone https://github.com/AfriGen-D/vcf-liftover.git
cd vcf-liftover
```

### 3. Test the Installation

Run the pipeline with test data to verify everything is working:

```bash
# Generate test data first
python3 bin/generate_test_data.py
python3 bin/generate_test_reference.py --regions chr21:1-10000000,chr22:1-20000000 --output test_data/GRCh38_test_regions.fa

# Run the pipeline with test data
nextflow run main.nf -profile test,singularity \
  --input test_data/small_chr22.vcf.gz \
  --target_fasta test_data/GRCh38_test_regions.fa
```

## What's Next?

- [Installation](/guide/installation) - Detailed installation instructions
- [Quick Start](/guide/quick-start) - Run your first analysis
- [Configuration](/guide/configuration) - Customize the pipeline for your needs

## Getting Help

If you encounter any issues:

1. Check the [troubleshooting guide](/guide/troubleshooting)
2. Search existing [GitHub issues](https://github.com/AfriGen-D/vcf-liftover/issues)
3. Create a new issue with details about your problem
4. Contact the AfriGen-D team at [AfriGen-D](https://afrigen-d.org)