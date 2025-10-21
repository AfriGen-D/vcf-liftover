# Installation

This page provides detailed installation instructions for {{ PROJECT_NAME }}.

## System Requirements

### Minimum Requirements

- **CPU**: {{ MIN_CPU_CORES }} cores
- **RAM**: {{ MIN_MEMORY }}GB
- **Storage**: {{ MIN_STORAGE }}GB free space
- **OS**: Linux, macOS, or Windows (with WSL2)

### Recommended Requirements

- **CPU**: {{ REC_CPU_CORES }} cores
- **RAM**: {{ REC_MEMORY }}GB
- **Storage**: {{ REC_STORAGE }}GB free space
- **Network**: High-speed internet for downloading references and containers

## Dependencies

### Core Dependencies

1. **Nextflow** (≥ {{ MIN_NEXTFLOW_VERSION }})
2. **Java** 11 or later
3. **Container engine** (choose one):
   - Docker (recommended)
   - Singularity/Apptainer
   - Conda/Mamba

### Optional Dependencies

- **Git** - for cloning the repository
- **curl/wget** - for downloading data

## Installation Methods

### Method 1: Using Docker (Recommended)

```bash
# Install Docker (Ubuntu/Debian)
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Nextflow
curl -s https://get.nextflow.io | bash
sudo mv nextflow /usr/local/bin/

# Clone and test
git clone https://github.com/AfriGen-D/{{ REPO_NAME }}.git
cd {{ REPO_NAME }}
nextflow run main.nf -profile test,docker
```

### Method 2: Using Singularity

```bash
# Install Singularity (varies by system)
# For CentOS/RHEL/Rocky Linux:
sudo yum install -y singularity-ce

# For Ubuntu:
sudo apt install -y singularity-container

# Install Nextflow
curl -s https://get.nextflow.io | bash
sudo mv nextflow /usr/local/bin/

# Clone and test
git clone https://github.com/AfriGen-D/{{ REPO_NAME }}.git
cd {{ REPO_NAME }}
nextflow run main.nf -profile test,singularity
```

### Method 3: Using Conda

```bash
# Install Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh

# Create environment
conda create -n nextflow -c bioconda nextflow
conda activate nextflow

# Clone and test
git clone https://github.com/AfriGen-D/{{ REPO_NAME }}.git
cd {{ REPO_NAME }}
nextflow run main.nf -profile test,conda
```

## HPC/Cluster Installation

### SLURM Clusters

```bash
# Load required modules
module load nextflow/{{ MIN_NEXTFLOW_VERSION }}
module load singularity

# Clone pipeline
git clone https://github.com/AfriGen-D/{{ REPO_NAME }}.git
cd {{ REPO_NAME }}

# Test with SLURM profile
nextflow run main.nf -profile test,slurm
```

### PBS/Torque Clusters

```bash
# Modify nextflow.config for PBS
# Add PBS executor configuration
nextflow run main.nf -profile test,pbs
```

## Cloud Installation

### AWS

```bash
# Configure AWS credentials
aws configure

# Run with AWS Batch
nextflow run main.nf -profile test,awsbatch \
  --outdir s3://your-bucket/results/
```

### Google Cloud

```bash
# Configure gcloud
gcloud auth login
gcloud config set project your-project-id

# Run with Google Life Sciences
nextflow run main.nf -profile test,gls \
  --outdir gs://your-bucket/results/
```

## Verification

After installation, verify everything is working:

```bash
# Check Nextflow version
nextflow -version

# Check container engine
docker --version
# OR
singularity --version

# Run pipeline test
cd {{ REPO_NAME }}
nextflow run main.nf -profile test
```

Expected output:
```
N E X T F L O W  ~  version {{ MIN_NEXTFLOW_VERSION }}
...
Pipeline completed successfully!
```

## Troubleshooting

### Common Issues

**Issue**: Nextflow command not found
```bash
# Solution: Add to PATH
export PATH="$HOME:$PATH"
```

**Issue**: Permission denied for Docker
```bash
# Solution: Add user to docker group
sudo usermod -aG docker $USER
# Log out and log back in
```

**Issue**: Java version conflicts
```bash
# Solution: Use specific Java version
export JAVA_HOME=/path/to/java11
export PATH="$JAVA_HOME/bin:$PATH"
```

For more troubleshooting tips, see the [troubleshooting guide](/guide/troubleshooting).

## Next Steps

- [Quick Start](/guide/quick-start) - Run your first analysis
- [Configuration](/guide/configuration) - Customize pipeline settings