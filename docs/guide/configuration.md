# Configuration

This page explains how to configure {{ PROJECT_NAME }} for different environments and use cases.

## Configuration Files

### nextflow.config

The main configuration file contains:

- Default parameters
- Process definitions
- Execution profiles
- Resource requirements

### profiles.config

Execution profiles for different environments:

- `docker` - Docker containers (default)
- `singularity` - Singularity containers
- `conda` - Conda environments
- `slurm` - SLURM executor
- `pbs` - PBS/Torque executor
- `awsbatch` - AWS Batch
- `gls` - Google Life Sciences

## Parameter Configuration

### Using Command Line

```bash
nextflow run main.nf \
  --input samples.csv \
  --outdir results/ \
  --{{ PARAM1 }} value1 \
  --{{ PARAM2 }} value2
```

### Using Parameters File

Create `params.yml`:

```yaml
# Input/Output
input: 'samples.csv'
outdir: 'results/'

# Reference genome
genome: '{{ DEFAULT_GENOME }}'

# Analysis parameters
{{ PARAM1 }}: value1
{{ PARAM2 }}: value2
{{ PARAM3 }}: value3

# Resource allocation
max_cpus: 16
max_memory: '64.GB'
max_time: '72.h'
```

Run with parameters file:

```bash
nextflow run main.nf -params-file params.yml
```

## Execution Profiles

### Local Profiles

#### Docker Profile (Default)

```groovy
docker {
    enabled = true
    userEmulation = true
    runOptions = '-u $(id -u):$(id -g)'
}
```

#### Singularity Profile

```groovy
singularity {
    enabled = true
    autoMounts = true
    cacheDir = "$HOME/.singularity_cache"
}
```

#### Conda Profile

```groovy
conda {
    enabled = true
    cacheDir = "$HOME/.conda_cache"
}
```

### HPC Profiles

#### SLURM Profile

```groovy
process {
    executor = 'slurm'
    queue = 'normal'
    clusterOptions = '--account=your_account'
}
```

#### PBS Profile

```groovy
process {
    executor = 'pbs'
    queue = 'normal'
}
```

### Cloud Profiles

#### AWS Batch Profile

```groovy
aws {
    region = 'us-east-1'
    batch {
        cliPath = '/usr/local/aws-cli/v2/current/bin/aws'
    }
}

process {
    executor = 'awsbatch'
    queue = 'nextflow-queue'
}
```

## Resource Configuration

### Per-Process Configuration

```groovy
process {
    // Default resources
    cpus = 1
    memory = '4.GB'
    time = '2.h'
    
    // Process-specific resources
    withName: 'PROCESS_NAME' {
        cpus = 8
        memory = '32.GB'
        time = '12.h'
    }
    
    withLabel: 'process_high_memory' {
        memory = '64.GB'
    }
}
```

### Global Resource Limits

```groovy
params {
    max_cpus = 16
    max_memory = '64.GB'
    max_time = '72.h'
}
```

## Custom Configuration

### Creating a Custom Profile

Create `conf/custom.config`:

```groovy
params {
    // Custom parameters
    custom_param = 'custom_value'
}

process {
    // Custom process configuration
    executor = 'local'
    cpus = 2
    memory = '8.GB'
}
```

Use with:

```bash
nextflow run main.nf -c conf/custom.config
```

### Institution-Specific Configs

For shared computing environments, create institution configs:

`conf/institution.config`:
```groovy
params {
    config_profile_description = 'Institution HPC cluster'
    config_profile_contact = 'admin@institution.edu'
    
    // Institution-specific defaults
    max_cpus = 128
    max_memory = '1.TB'
    max_time = '168.h'
}

process {
    executor = 'slurm'
    queue = 'genomics'
    clusterOptions = '--account=genomics_project'
}
```

## Environment Variables

Set environment variables for the pipeline:

```bash
export NXF_OPTS='-Xms1g -Xmx4g'
export NXF_SINGULARITY_CACHEDIR=$HOME/.singularity_cache
export TOWER_ACCESS_TOKEN=your_token_here

nextflow run main.nf --input samples.csv --outdir results/
```

## Troubleshooting Configuration

### Debug Mode

Enable debug mode for configuration issues:

```bash
nextflow run main.nf --input samples.csv -with-trace -with-report -with-timeline
```

### Dry Run

Test configuration without running processes:

```bash
nextflow run main.nf --input samples.csv -preview
```

### Configuration Validation

Check parameter validation:

```bash
nextflow run main.nf --help
```

## Best Practices

1. **Version Control**: Keep configuration files in version control
2. **Documentation**: Document custom configurations
3. **Testing**: Test configurations with small datasets
4. **Resource Limits**: Set appropriate resource limits
5. **Profiles**: Use profiles for different environments
6. **Security**: Don't hardcode credentials in config files

## Examples

See the [examples section](/examples/) for complete configuration examples for different use cases.