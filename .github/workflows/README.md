# GitHub Actions Workflows

This directory contains automated CI/CD workflows for the vcf-liftover pipeline.

## Workflows Overview

### 🧪 [ci.yml](ci.yml) - Continuous Integration

**Triggers**: Push/PR to `main` or `dev` branches

**Jobs**:
- **Pipeline Tests**: Tests pipeline with multiple Nextflow versions (23.04.0, 24.04.0, latest)
- **Python Tests**: Validates all Python scripts compile and are executable
- **Nextflow Lint**: Checks Nextflow syntax and configuration
- **Integration Test**: End-to-end test with small dataset

**Duration**: ~10-15 minutes

**Artifacts**: Test results, logs (7 days retention)

### 🐍 [python-lint.yml](python-lint.yml) - Python Code Quality

**Triggers**: Push/PR to `main`/`dev` when Python files change

**Jobs**:
- **Linting**: Flake8, Pylint, Black, isort checks
- **Security**: Bandit security scanning
- **Type Checking**: MyPy static type analysis
- **Documentation**: Pydocstyle docstring validation

**Duration**: ~3-5 minutes

**Artifacts**: Security reports (30 days retention)

### 🔧 [nextflow-lint.yml](nextflow-lint.yml) - Nextflow Code Quality

**Triggers**: Push/PR to `main`/`dev` when `.nf` or `.config` files change

**Jobs**:
- **Nextflow Lint**: Validates workflow and module syntax
- **Config Lint**: Validates configuration files and profiles
- **Dependencies**: Checks required files and chain files
- **Documentation Sync**: Validates README and test data

**Duration**: ~2-4 minutes

### 🚀 [release.yml](release.yml) - Automated Releases

**Triggers**:
- Push tags matching `v*.*.*` (e.g., v1.2.0)
- Manual workflow dispatch

**Jobs**:
- **Validate Tag**: Ensures version format is correct
- **Build and Test**: Full pipeline test before release
- **Create Release**: Generates GitHub release with changelog
- **Notify**: Release notification
- **Update Documentation**: Updates version in docs

**Duration**: ~10-15 minutes

### 📚 [deploy.yml](deploy.yml) - Documentation Deployment

**Triggers**: Push/PR to `main` when `docs/` changes

**Jobs**:
- **Build**: Builds VitePress documentation
- **Deploy**: Deploys to GitHub Pages (main branch only)

**Duration**: ~2-3 minutes

## Workflow Status Badges

Add these to your README.md:

```markdown
[![CI Tests](https://github.com/AfriGen-D/vcf-liftover/actions/workflows/ci.yml/badge.svg)](https://github.com/AfriGen-D/vcf-liftover/actions/workflows/ci.yml)
[![Python Lint](https://github.com/AfriGen-D/vcf-liftover/actions/workflows/python-lint.yml/badge.svg)](https://github.com/AfriGen-D/vcf-liftover/actions/workflows/python-lint.yml)
[![Nextflow Lint](https://github.com/AfriGen-D/vcf-liftover/actions/workflows/nextflow-lint.yml/badge.svg)](https://github.com/AfriGen-D/vcf-liftover/actions/workflows/nextflow-lint.yml)
```

## Local Testing

Before pushing, test your changes locally:

### Test Pipeline
```bash
# Run full test
nextflow run main.nf -profile test,docker

# Quick syntax check
nextflow run main.nf --help
```

### Test Python Scripts
```bash
# Syntax check
python -m py_compile bin/*.py

# Format code
black bin/*.py
isort bin/*.py

# Lint
flake8 bin/*.py
pylint bin/*.py
```

### Test Nextflow Config
```bash
# Validate config
nextflow config main.nf -profile test,docker

# Show all profiles
nextflow config -show-profiles main.nf
```

## Workflow Configuration

### Required Secrets

No secrets required for basic workflows. All workflows use:
- `GITHUB_TOKEN` (automatically provided by GitHub)

### Optional Enhancements

For advanced features, you can add:

- **Slack Notifications**: Add `SLACK_WEBHOOK` secret
- **Email Notifications**: Configure in repository settings
- **Container Registry**: Add `DOCKER_HUB_TOKEN` for pushing containers

## Troubleshooting

### Workflow Fails on Docker Setup
- **Issue**: Docker setup fails in GitHub Actions
- **Solution**: Check if `docker/setup-buildx-action@v3` is up to date

### Tests Pass Locally but Fail in CI
- **Issue**: Path or dependency differences
- **Solution**: Use absolute paths and check container bindings

### Python Linting Failures
- **Issue**: Black/isort formatting issues
- **Solution**: Run `black bin/*.py && isort bin/*.py` locally

### Nextflow Version Mismatch
- **Issue**: Pipeline works with newer Nextflow but fails with older
- **Solution**: Update minimum version in `nextflow.config`

## Best Practices

1. **Always test locally** before pushing
2. **Run formatters** (Black, isort) before committing Python code
3. **Use descriptive commit messages** for better changelog generation
4. **Tag releases** with semantic versioning (v1.2.3)
5. **Update documentation** when adding new features

## Maintenance

### Updating Workflow Dependencies

Update action versions periodically:

```yaml
# Check for updates
uses: actions/checkout@v4  # Latest
uses: actions/setup-python@v4  # Latest
uses: nf-core/setup-nextflow@v1  # Latest
```

### Adding New Tests

To add new tests:

1. Add test to appropriate workflow file
2. Test locally if possible
3. Create PR and verify in CI
4. Merge after successful runs

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Nextflow Documentation](https://www.nextflow.io/docs/latest/index.html)
- [nf-core Best Practices](https://nf-co.re/docs/contributing/guidelines)

## Support

For workflow issues:
- Open an issue with the `ci/cd` label
- Check workflow logs in the Actions tab
- Contact: mamana.mbiyavanga@uct.ac.za
