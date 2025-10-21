<div align="center">
  <img src="https://raw.githubusercontent.com/AfriGen-D/afrigen-d-templates/main/assets/afrigen-d-logo.png" alt="AfriGen-D Logo" width="200" />
  <h1>VCF Liftover</h1>
</div>

<div align="center">

[![Nextflow](https://img.shields.io/badge/nextflow%20DSL2-%E2%89%A522.10.1-23aa62.svg)](https://www.nextflow.io/)
[![run with conda](http://img.shields.io/badge/run%20with-conda-3EB049?labelColor=000000&logo=anaconda)](https://docs.conda.io/en/latest/)
[![run with docker](https://img.shields.io/badge/run%20with-docker-0db7ed?labelColor=000000&logo=docker)](https://www.docker.com/)
[![run with singularity](https://img.shields.io/badge/run%20with-singularity-1d355c.svg?labelColor=000000)](https://sylabs.io/docs/)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://afrigen-d.github.io/vcf-liftover)

</div>

## Introduction

**VCF Liftover** is a bioinformatics best-practice analysis pipeline for converting genomic coordinates between different genome builds. The pipeline is designed to work with VCF files and produces lifted-over VCF files with comprehensive quality control and validation reports.

The pipeline is built using [Nextflow](https://www.nextflow.io), a workflow tool to run tasks across multiple compute environments in a very portable manner. It uses Docker/Singularity containers making installation trivial and results highly reproducible.

## Pipeline Summary

VCF Liftover performs the following steps:

1. **Input Validation** - Verify VCF files are properly formatted and indexed
2. **Chromosome Validation** - Check chromosome naming compatibility with target genome
3. **Coordinate Liftover** - Convert genomic coordinates using CrossMap
4. **Automatic Chromosome Renaming** - Smart detection and correction of chromosome naming differences
5. **VCF Sorting & Compression** - Sort and compress output VCF files
6. **Quality Control** - Generate statistics and validation reports
7. **Results Aggregation** - Combine outputs and generate comprehensive HTML reports

## Quick Start

```bash
# Clone the repository
git clone https://github.com/AfriGen-D/vcf-liftover.git
cd vcf-liftover

# Run with test data
nextflow run main.nf -profile test,singularity

# Run with your data
nextflow run main.nf \
    --input your_file.vcf.gz \
    --target_fasta /path/to/GRCh38.fa \
    -profile singularity
```

## Project Structure

```
vcf-liftover/
├── main.nf                 # Main pipeline script
├── nextflow.config         # Pipeline configuration
├── modules/                # Process modules
├── workflows/              # Workflow definitions
├── conf/                   # Configuration profiles
├── bin/                    # Utility scripts
├── assets/                 # Pipeline assets
├── chains/                 # Chain files for liftover
├── test_data/              # Test datasets for validation
│   ├── config/             # CSV batch files and configuration
│   ├── hg19/              # Source genome (hg19) test files
│   │   └── vcf/           # Test VCF files
│   └── hg38/              # Target genome (hg38) reference files
│       └── reference/     # Test reference genomes
└── docs/                   # User documentation (VitePress)
```

## Documentation

📖 **Complete documentation is available at: [https://afrigen-d.github.io/vcf-liftover](https://afrigen-d.github.io/vcf-liftover)**

The documentation includes:

- **[Quick Start Tutorial](https://afrigen-d.github.io/vcf-liftover/tutorials/quick-start)** - Get started in 5 minutes
- **[Complete Reference](https://afrigen-d.github.io/vcf-liftover/reference/)** - All parameters and options
- **[Step-by-Step Tutorials](https://afrigen-d.github.io/vcf-liftover/tutorials/)** - Learn with guided examples
- **[Understanding Results](https://afrigen-d.github.io/vcf-liftover/docs/understanding-results)** - Interpret your output

## Requirements

- **Nextflow** ≥ 22.10.1
- **Singularity** or **Docker**
- **Target reference genome** (e.g., GRCh38)

## Development & Contributing

Interested in contributing? See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Cleanup After Pipeline Runs

The pipeline generates temporary files that should be cleaned up before committing changes:

```bash
# Clean up temporary files
rm -rf work/ .nextflow .nextflow.log* results/ test_results/ benchmark_results/
```

These directories can be several GB in size and are automatically ignored by git (see [.gitignore](.gitignore)).

## Credits

VCF Liftover was originally written by Mamana Mbiyavanga.

We thank the following people for their extensive assistance in the development of this pipeline:

- AfriGen-D project members and collaborators
- The nf-core community for best practices and tools
- CrossMap developers for the liftover tool

## Contributions and Support

If you would like to contribute to this pipeline, please see the [contributing guidelines](CONTRIBUTING.md).

For further information or help, don't hesitate to get in touch:

- **[Discussions](https://github.com/orgs/AfriGen-D/discussions)**: Community Q&A and feature requests
- **[Issues](https://github.com/AfriGen-D/vcf-liftover/issues)**: Bug reports and technical issues
- **Helpdesk**: [helpdesk.afrigen-d.org](https://helpdesk.afrigen-d.org)
- **Website**: [afrigen-d.org](https://afrigen-d.org)

## Citations

If you use VCF Liftover for your analysis, please cite:

```bibtex
@software{vcf_liftover,
  title = {VCF Liftover},
  author = {Mbiyavanga, Mamana},
  year = {2025},
  url = {https://github.com/AfriGen-D/vcf-liftover}
}
```

An extensive list of references for the tools used by the pipeline can be found in the [`CITATIONS.md`](CITATIONS.md) file.

This pipeline uses code and infrastructure developed and maintained by the [nf-core](https://nf-co.re) initiative, and reused here under the [MIT license](https://github.com/nf-core/tools/blob/master/LICENSE).

> **The nf-core framework for community-curated bioinformatics pipelines.**
>
> Philip Ewels, Alexander Peltzer, Sven Fillinger, Holger Hoeft, Johannes Alneberg, Maxime Ulysse Garcia, Paolo Di Tommaso & Sven Nahnsen.
>
> _Nat Biotechnol._ 2020 Feb 13. doi: [10.1038/s41587-020-0439-x](https://dx.doi.org/10.1038/s41587-020-0439-x).

## About AfriGen-D

AfriGen-D is a project dedicated to enabling innovation in African genomics research through:

- **Research Tools**: Cutting-edge bioinformatics software
- **Data Resources**: Curated genomic datasets and reference panels
- **Community**: Collaborative research networks
- **Education**: Training and capacity building

Visit [afrigen-d.org](https://afrigen-d.org) to learn more about our mission and projects.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- AfriGen-D project members and collaborators
- Contributing researchers and developers
- Supporting institutions and funding agencies
- The broader genomics and open science communities

---

<div align="center">
  <p><strong>Enabling innovation in African genomics research</strong></p>
  <p>
    <a href="https://afrigen-d.org">Website</a> •
    <a href="https://twitter.com/AfriGenD">Twitter</a> •
    <a href="https://linkedin.com/company/afrigen-d">LinkedIn</a> •
    <a href="https://youtube.com/@afrigen-d">YouTube</a>
  </p>
</div>
