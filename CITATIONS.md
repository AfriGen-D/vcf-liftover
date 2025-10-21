# Citations

## Pipeline Tools

This pipeline uses the following tools and software. If you use this pipeline in your research, please cite the relevant publications.

### Core Tools

#### CrossMap
> **CrossMap: a versatile tool for coordinate conversion between genome assemblies**
>
> Zhao H, Sun Z, Wang J, Huang H, Kocher JP, Wang L.
>
> _Bioinformatics._ 2014 Apr 15;30(8):1006-7. doi: [10.1093/bioinformatics/btt730](https://doi.org/10.1093/bioinformatics/btt730)

```bibtex
@article{crossmap2014,
  title={CrossMap: a versatile tool for coordinate conversion between genome assemblies},
  author={Zhao, Haiyan and Sun, Zhi and Wang, Jie and Huang, Hongfei and Kocher, Jean-Pierre and Wang, Liguo},
  journal={Bioinformatics},
  volume={30},
  number={8},
  pages={1006--1007},
  year={2014},
  publisher={Oxford University Press},
  doi={10.1093/bioinformatics/btt730}
}
```

#### Nextflow
> **Nextflow enables reproducible computational workflows**
>
> Paolo Di Tommaso, Maria Chatzou, Evan W Floden, Pablo Prieto Barja, Emilio Palumbo, Cedric Notredame.
>
> _Nat Biotechnol._ 2017 Apr 11;35(4):316-319. doi: [10.1038/nbt.3820](https://doi.org/10.1038/nbt.3820)

```bibtex
@article{ditommaso2017nextflow,
  title={Nextflow enables reproducible computational workflows},
  author={Di Tommaso, Paolo and Chatzou, Maria and Floden, Evan W and Barja, Pablo Prieto and Palumbo, Emilio and Notredame, Cedric},
  journal={Nature biotechnology},
  volume={35},
  number={4},
  pages={316--319},
  year={2017},
  publisher={Nature Publishing Group},
  doi={10.1038/nbt.3820}
}
```

### Workflow Framework

#### nf-core
> **The nf-core framework for community-curated bioinformatics pipelines**
>
> Philip Ewels, Alexander Peltzer, Sven Fillinger, Holger Patzl, Johannes Alneberg, Andreas Wilm, Maxime Ulysse Garcia, Paolo Di Tommaso, Sven Nahnsen.
>
> _Nat Biotechnol._ 2020 Feb 13;38(3):276-278. doi: [10.1038/s41587-020-0439-x](https://doi.org/10.1038/s41587-020-0439-x)

```bibtex
@article{ewels2020nf,
  title={The nf-core framework for community-curated bioinformatics pipelines},
  author={Ewels, Philip A and Peltzer, Alexander and Fillinger, Sven and Patzl, Holger and Alneberg, Johannes and Wilm, Andreas and Garcia, Maxime Ulysse and Di Tommaso, Paolo and Nahnsen, Sven},
  journal={Nature biotechnology},
  volume={38},
  number={3},
  pages={276--278},
  year={2020},
  publisher={Nature Publishing Group},
  doi={10.1038/s41587-020-0439-x}
}
```

### Data Processing Tools

#### BCFtools
> **Twelve years of SAMtools and BCFtools**
>
> Petr Danecek, James K Bonfield, Jennifer Liddle, John Marshall, Valeriu Ohan, Martin O Pollard, Andrew Whitwham, Thomas Keane, Shane A McCarthy, Robert M Davies, Heng Li.
>
> _GigaScience._ 2021 Feb 16;10(2):giab008. doi: [10.1093/gigascience/giab008](https://doi.org/10.1093/gigascience/giab008)

```bibtex
@article{danecek2021twelve,
  title={Twelve years of SAMtools and BCFtools},
  author={Danecek, Petr and Bonfield, James K and Liddle, Jennifer and Marshall, John and Ohan, Valeriu and Pollard, Martin O and Whitwham, Andrew and Keane, Thomas and McCarthy, Shane A and Davies, Robert M and others},
  journal={Gigascience},
  volume={10},
  number={2},
  pages={giab008},
  year={2021},
  publisher={Oxford University Press},
  doi={10.1093/gigascience/giab008}
}
```

#### SAMtools
> **The Sequence Alignment/Map format and SAMtools**
>
> Heng Li, Bob Handsaker, Alec Wysoker, Tim Fennell, Jue Ruan, Nils Homer, Gabor Marth, Goncalo Abecasis, Richard Durbin, 1000 Genome Project Data Processing Subgroup.
>
> _Bioinformatics._ 2009 Aug 15;25(16):2078-9. doi: [10.1093/bioinformatics/btp352](https://doi.org/10.1093/bioinformatics/btp352)

```bibtex
@article{li2009sequence,
  title={The sequence alignment/map format and SAMtools},
  author={Li, Heng and Handsaker, Bob and Wysoker, Alec and Fennell, Tim and Ruan, Jue and Homer, Nils and Marth, Gabor and Abecasis, Goncalo and Durbin, Richard},
  journal={Bioinformatics},
  volume={25},
  number={16},
  pages={2078--2079},
  year={2009},
  publisher={Oxford University Press},
  doi={10.1093/bioinformatics/btp352}
}
```

### Containerization

#### Docker
> **Docker: lightweight linux containers for consistent development and deployment**
>
> Dirk Merkel.
>
> _Linux Journal._ 2014 Mar;2014(239):2.

#### Singularity
> **Singularity: Scientific containers for mobility of compute**
>
> Gregory M. Kurtzer, Vanessa Sochat, Michael W. Bauer.
>
> _PLoS ONE._ 2017 May 11;12(5):e0177459. doi: [10.1371/journal.pone.0177459](https://doi.org/10.1371/journal.pone.0177459)

```bibtex
@article{kurtzer2017singularity,
  title={Singularity: Scientific containers for mobility of compute},
  author={Kurtzer, Gregory M and Sochat, Vanessa and Bauer, Michael W},
  journal={PloS one},
  volume={12},
  number={5},
  pages={e0177459},
  year={2017},
  publisher={Public Library of Science San Francisco, CA USA},
  doi={10.1371/journal.pone.0177459}
}
```

## Software Versions

For reproducibility, the specific versions of all tools used in this pipeline are documented in the container definitions and Nextflow configuration files.

## Citing This Pipeline

If you use VCF Liftover in your research, please cite:

```bibtex
@software{vcf_liftover,
  title = {VCF Liftover},
  author = {Mbiyavanga, Mamana},
  year = {2025},
  url = {https://github.com/AfriGen-D/vcf-liftover},
  organization = {AfriGen-D}
}
```

## Reference Genomes

Depending on your analysis, please also cite the appropriate reference genome:

### GRCh37/hg19
> **Initial sequencing and analysis of the human genome**
>
> International Human Genome Sequencing Consortium.
>
> _Nature._ 2001 Feb 15;409(6822):860-921. doi: [10.1038/35057062](https://doi.org/10.1038/35057062)

### GRCh38/hg38
> **The DNA sequence and analysis of human chromosome 13**
>
> Genome Reference Consortium.
>
> _Nature._ 2004 Apr 1;428(6982):522-528. doi: [10.1038/nature02379](https://doi.org/10.1038/nature02379)

## Chain Files

Chain files for genome liftover are provided by UCSC Genome Browser:

> **The UCSC Genome Browser database: 2021 update**
>
> Navya S. Lee, Jonathan Casper, Brian J. Raney, Matthew L. Speir, Robert M. Kuhn, Ann S. Clawson, Hiram Clawson, Brooke Rhead, W. James Kent.
>
> _Nucleic Acids Research._ 2021 Jan 8;49(D1):D1046-D1057. doi: [10.1093/nar/gkaa1070](https://doi.org/10.1093/nar/gkaa1070)

---

**Note**: This citation list may not be exhaustive. Additional tools and dependencies may be used depending on the specific configuration and parameters used in your analysis.
