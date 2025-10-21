# Execution Profiles ​

vcf-liftover provides multiple execution profiles to support different computing environments and container technologies.

## Available Profiles ​

### Container Profiles ​

#### Singularity Profile ​
**Recommended for HPC environments**

```bash
nextflow run main.nf -profile singularity \
  --input sample.vcf.gz \
  --target_fasta GRCh38.fa
```

**Features:**
- Uses Singularity containers for all processes
- Automatically pulls containers from registries
- Ideal for HPC clusters and shared systems
- No root privileges required

**Configuration:**
```groovy
singularity {
  enabled = true
  autoMounts = true
  cacheDir = "$HOME/.singularity/cache"
}
```

#### Docker Profile ​
**Recommended for local development**

```bash
nextflow run main.nf -profile docker \
  --input sample.vcf.gz \
  --target_fasta GRCh38.fa
```

**Features:**
- Uses Docker containers for all processes
- Fast container startup times
- Ideal for local development and testing
- Requires Docker daemon running

**Configuration:**
```groovy
docker {
  enabled = true
  runOptions = '-u $(id -u):$(id -g)'
}
```

#### Conda Profile ​
**Alternative for environments without containers**

```bash
nextflow run main.nf -profile conda \
  --input sample.vcf.gz \
  --target_fasta GRCh38.fa
```

**Features:**
- Uses Conda environments for dependencies
- No container technology required
- Automatic environment creation
- Cross-platform compatibility

### Executor Profiles ​

#### Local Profile ​
**Default execution on local machine**

```bash
nextflow run main.nf -profile local,singularity \
  --input sample.vcf.gz \
  --target_fasta GRCh38.fa
```

**Features:**
- Executes all processes locally
- Uses available CPU cores
- Suitable for small datasets
- No job scheduler required

#### SLURM Profile ​
**For SLURM-managed HPC clusters**

```bash
nextflow run main.nf -profile slurm,singularity \
  --input sample.vcf.gz \
  --target_fasta GRCh38.fa
```

**Features:**
- Submits jobs to SLURM scheduler
- Automatic resource allocation
- Queue management
- Parallel job execution

**Configuration:**
```groovy
process {
  executor = 'slurm'
  queue = 'normal'
  clusterOptions = '--account=myaccount'
}
```

#### PBS Profile ​
**For PBS/Torque-managed clusters**

```bash
nextflow run main.nf -profile pbs,singularity \
  --input sample.vcf.gz \
  --target_fasta GRCh38.fa
```

**Features:**
- Submits jobs to PBS scheduler
- Resource allocation via PBS
- Queue-based job management

### Test Profiles ​

#### Test Profile ​
**Quick validation with test data**

```bash
nextflow run main.nf -profile test,singularity
```

**Features:**
- Uses built-in test dataset
- Validates pipeline functionality
- Quick execution (< 5 minutes)
- No input parameters required

**Included test data:**
- Small VCF file (chr22 subset)
- Test reference FASTA
- Expected output for validation

## Profile Combinations ​

### Recommended Combinations ​

#### HPC with Singularity ​
```bash
-profile singularity,slurm
```
- Best for production HPC environments
- Combines container isolation with job scheduling
- Scalable for large datasets

#### Local Development ​
```bash
-profile docker,local
```
- Ideal for testing and development
- Fast iteration cycles
- Easy debugging

#### Cloud Environments ​
```bash
-profile singularity,awsbatch
```
- Scalable cloud execution
- Cost-effective for large analyses
- Automatic resource provisioning

### Custom Profile Combinations ​

You can combine multiple profiles:

```bash
# Multiple container and executor profiles
nextflow run main.nf -profile singularity,slurm,test

# Custom resource allocation
nextflow run main.nf -profile docker,local \
  --max_cpus 8 \
  --max_memory '32.GB'
```

## Profile Configuration ​

### Creating Custom Profiles ​

Add to your `nextflow.config`:

```groovy
profiles {
  myprofile {
    process {
      executor = 'slurm'
      queue = 'gpu'
      cpus = 8
      memory = '32.GB'
      time = '4.h'
    }
    
    singularity {
      enabled = true
      cacheDir = '/shared/singularity'
    }
  }
}
```

### Environment-Specific Settings ​

#### For HPC Clusters ​
```groovy
profiles {
  cluster {
    process {
      executor = 'slurm'
      queue = 'normal'
      clusterOptions = '--account=genomics --partition=compute'
      
      withName: CROSSMAP_LIFTOVER {
        cpus = 4
        memory = '16.GB'
        time = '2.h'
      }
      
      withName: SORT_VCF {
        cpus = 2
        memory = '8.GB'
        time = '1.h'
      }
    }
  }
}
```

#### For Cloud Environments ​
```groovy
profiles {
  aws {
    process {
      executor = 'awsbatch'
      queue = 'genomics-queue'
      container = 'your-ecr-repo/vcf-liftover'
    }
    
    aws {
      region = 'us-east-1'
      batch {
        cliPath = '/home/ec2-user/miniconda/bin/aws'
      }
    }
  }
}
```

## Resource Allocation ​

### Default Resource Limits ​

```groovy
params {
  max_cpus = 16
  max_memory = '128.GB'
  max_time = '240.h'
}
```

### Process-Specific Resources ​

```groovy
process {
  withName: CROSSMAP_LIFTOVER {
    cpus = { check_max(4, 'cpus') }
    memory = { check_max(16.GB * task.attempt, 'memory') }
    time = { check_max(2.h * task.attempt, 'time') }
  }
  
  withName: SORT_VCF {
    cpus = { check_max(2, 'cpus') }
    memory = { check_max(8.GB * task.attempt, 'memory') }
    time = { check_max(1.h * task.attempt, 'time') }
  }
}
```

## Troubleshooting Profiles ​

### Common Issues ​

#### Container Not Found ​
```bash
# Check container availability
singularity pull docker://quay.io/biocontainers/crossmap:0.6.4--py39h5371cbf_0

# Verify Docker daemon
docker info
```

#### Scheduler Issues ​
```bash
# Check SLURM availability
sinfo

# Verify PBS status
qstat -Q
```

#### Permission Issues ​
```bash
# Fix Singularity cache permissions
chmod -R 755 $HOME/.singularity

# Check Docker group membership
groups $USER
```

### Profile Validation ​

Test your profile configuration:

```bash
# Dry run to validate configuration
nextflow run main.nf -profile yourprofile --help

# Test with minimal data
nextflow run main.nf -profile yourprofile,test
```

## Best Practices ​

### Profile Selection ​

1. **Development**: Use `docker,local` for fast iteration
2. **Testing**: Use `test,singularity` for validation
3. **Production**: Use `singularity,slurm` for scalability
4. **Cloud**: Use `singularity,awsbatch` for cloud deployment

### Resource Planning ​

1. **Start small**: Begin with default resources
2. **Monitor usage**: Check actual resource consumption
3. **Scale up**: Increase resources for large datasets
4. **Optimize**: Fine-tune based on performance metrics

### Container Management ​

1. **Cache containers**: Use persistent cache directories
2. **Pre-pull images**: Download containers before large runs
3. **Version pinning**: Use specific container versions for reproducibility
4. **Local registry**: Consider local container registries for frequent use

## Related Resources ​

- [Configuration](/reference/configuration) - Advanced configuration options
- [Parameters](/reference/parameters) - Complete parameter reference
- [Tutorials](/tutorials/) - Hands-on profile usage examples
