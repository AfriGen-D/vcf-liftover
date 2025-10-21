# Chain Files for Genome Liftover

This directory contains chain files for coordinate conversion between different genome assemblies. These files are used by CrossMap and other liftover tools to convert genomic coordinates from one reference genome to another.

## Available Chain Files

### Human Genome Assemblies

#### hg17 (NCBI Build 35, May 2004)
- `hg17ToHg18.over.chain.gz` - hg17 to hg18 conversion
- `hg17ToHg19.over.chain.gz` - hg17 to hg19 conversion

#### hg18 (NCBI Build 36, March 2006)
- `hg18ToHg19.over.chain.gz` - hg18 to hg19 conversion
- `hg18ToHg38.over.chain.gz` - hg18 to hg38 conversion

#### hg19 (GRCh37, February 2009)
- `hg19ToHg18.over.chain.gz` - hg19 to hg18 conversion
- `hg19ToHg38.over.chain.gz` - hg19 to hg38 conversion (most commonly used)

#### hg38 (GRCh38, December 2013)
- `hg38ToHg19.over.chain.gz` - hg38 to hg19 conversion

### Mouse Genome Assemblies

#### mm9 (NCBI Build 37, July 2007)
- `mm9ToMm10.over.chain.gz` - mm9 to mm10 conversion

#### mm10 (GRCm38, December 2011)
- `mm10ToMm9.over.chain.gz` - mm10 to mm9 conversion

### Test Files
- `hg19ToHg38.test.chain.gz` - Minimal test chain file for pipeline testing

## Usage Examples

### Basic Liftover (hg19 to hg38)
```bash
nextflow run main.nf \
    -profile singularity \
    --input samples.csv \
    --chain_file chains/hg19ToHg38.over.chain.gz \
    --target_fasta hg38.fa
```

### Reverse Liftover (hg38 to hg19)
```bash
nextflow run main.nf \
    -profile singularity \
    --input samples.csv \
    --chain_file chains/hg38ToHg19.over.chain.gz \
    --target_fasta hg19.fa \
    --source_build hg38 \
    --target_build hg19
```

### Mouse Genome Liftover
```bash
nextflow run main.nf \
    -profile singularity \
    --input mouse_samples.csv \
    --chain_file chains/mm9ToMm10.over.chain.gz \
    --target_fasta mm10.fa \
    --source_build mm9 \
    --target_build mm10
```

## File Information

| Chain File | Source | Target | Size | Date |
|------------|--------|--------|------|------|
| hg17ToHg18.over.chain.gz | hg17 | hg18 | 83K | 2006 |
| hg17ToHg19.over.chain.gz | hg17 | hg19 | 147K | 2006 |
| hg18ToHg19.over.chain.gz | hg18 | hg19 | 137K | 2007 |
| hg18ToHg38.over.chain.gz | hg18 | hg38 | 336K | 2014 |
| hg19ToHg18.over.chain.gz | hg19 | hg18 | 221K | 2014 |
| hg19ToHg38.over.chain.gz | hg19 | hg38 | 222K | 2014 |
| hg38ToHg19.over.chain.gz | hg38 | hg19 | 1.2M | 2014 |
| mm9ToMm10.over.chain.gz | mm9 | mm10 | 523K | 2012 |
| mm10ToMm9.over.chain.gz | mm10 | mm9 | 940K | 2012 |

## Adding New Chain Files

To add new chain files:

1. Download from UCSC Genome Browser:
   ```bash
   wget -O newChain.over.chain.gz http://hgdownload.cse.ucsc.edu/goldenpath/[source]/liftOver/[source]To[target].over.chain.gz
   ```

2. Place in this directory
3. Update this README with the new file information

## Common UCSC Download URLs

- **Human genomes**: `http://hgdownload.cse.ucsc.edu/goldenpath/[build]/liftOver/`
- **Mouse genomes**: `http://hgdownload.cse.ucsc.edu/goldenpath/[build]/liftOver/`
- **Other species**: Check UCSC Genome Browser downloads section

## Notes

- Chain files are specific to the direction of conversion (source → target)
- For bidirectional conversion, you need both chain files
- File sizes vary based on the complexity of rearrangements between assemblies
- Always verify the chain file matches your source and target genome builds
- Test with a small dataset before running large-scale liftover operations

## References

- [UCSC Genome Browser LiftOver](https://genome.ucsc.edu/cgi-bin/hgLiftOver)
- [CrossMap Documentation](https://crossmap.readthedocs.io/)
- [Chain File Format Specification](https://genome.ucsc.edu/goldenPath/help/chain.html)
