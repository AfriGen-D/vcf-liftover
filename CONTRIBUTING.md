# Contributing to VCF Liftover

Thank you for your interest in contributing to VCF Liftover! We welcome contributions from researchers, developers, and the broader genomics community.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Please treat all community members with respect and create a welcoming environment for everyone.

## Development Workflow

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR-USERNAME/vcf-liftover.git
cd vcf-liftover
```

### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 3. Make Your Changes

Follow the coding standards and test your changes thoroughly.

### 4. Test Your Changes

```bash
# Run with test profile
nextflow run main.nf -profile test,singularity

# Run with different configurations if applicable
nextflow run main.nf -profile test,docker
```

### 5. **IMPORTANT: Clean Up Before Committing**

**Always clean temporary files before committing:**

```bash
# Required cleanup before every commit
rm -rf work/ .nextflow .nextflow.log* results/ test_results/ benchmark_results/
```

**Why this matters:**
- Nextflow `work/` directories can be several GB in size
- Log files accumulate over multiple runs
- Generated outputs should not be committed to the repository
- Keeps the repository clean and focused on source code

### 6. Commit Your Changes

```bash
git add .
git commit -m "feat: descriptive commit message"
```

Use conventional commit messages:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test additions or modifications
- `refactor:` - Code refactoring
- `ci:` - CI/CD changes

### 7. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Coding Standards

### Nextflow Code

- Follow [nf-core style guidelines](https://nf-co.re/docs/contributing/guidelines)
- Use meaningful process and variable names
- Add comments for complex logic
- Keep processes modular and reusable
- Use proper indentation (4 spaces)

Example:
```nextflow
process EXAMPLE_PROCESS {
    tag "$sample_id"
    publishDir "${params.outdir}/process_name", mode: 'copy'

    input:
    tuple val(sample_id), path(input_file)

    output:
    tuple val(sample_id), path("${sample_id}.output")

    script:
    """
    # Process the input file
    process_command ${input_file} > ${sample_id}.output
    """
}
```

### Python Scripts

- Place scripts in the `bin/` directory
- Follow PEP 8 style guide
- Include docstrings for functions and modules
- Use type hints where applicable
- Add argument parsing with helpful descriptions

Example:
```python
#!/usr/bin/env python3
"""
Brief description of what this script does.
"""

import argparse
from typing import List

def process_data(input_path: str, output_path: str) -> None:
    """
    Process the input data and write results.

    Args:
        input_path: Path to input file
        output_path: Path to output file
    """
    # Implementation here
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Input file path")
    parser.add_argument("--output", required=True, help="Output file path")
    args = parser.parse_args()

    process_data(args.input, args.output)
```

### Configuration Files

- Keep `nextflow.config` clean and well-organized
- Use profile-specific configs in `conf/` directory
- Document non-obvious configuration options
- Follow Nextflow configuration best practices

## Testing

### Local Testing

Always test your changes locally before pushing:

```bash
# Test with Singularity
nextflow run main.nf -profile test,singularity

# Test with Docker
nextflow run main.nf -profile test,docker

# Test with resume
nextflow run main.nf -profile test,singularity -resume

# Generate execution reports
nextflow run main.nf -profile test,singularity \
    -with-report report.html \
    -with-trace trace.txt \
    -with-timeline timeline.html
```

### Continuous Integration

The project uses GitHub Actions for CI/CD:
- Code is automatically tested on pull requests
- Linting checks are performed (Nextflow, Python)
- Tests must pass before merging

## Documentation

### Update Documentation When:

1. Adding new parameters or options
2. Changing pipeline behavior
3. Adding new features
4. Fixing bugs that affect usage

### Documentation Files

- `README.md` - Main project overview
- `docs/` - VitePress documentation site
  - `docs/guide/` - User guides
  - `docs/reference/` - Parameter reference
  - `docs/tutorials/` - Step-by-step tutorials
- `CLAUDE.md` - Instructions for Claude AI assistant
- `CONTRIBUTING.md` - This file

### Building Documentation Locally

```bash
cd docs
npm install
npm run docs:dev
```

Visit http://localhost:5173 to preview documentation.

## Cleanup Checklist

Before committing, ensure you've done the following:

- [ ] Removed `work/` directory
- [ ] Removed `.nextflow/` and `.nextflow.log*` files
- [ ] Removed `results/`, `test_results/`, `benchmark_results/` directories
- [ ] Tested your changes with test profile
- [ ] Updated documentation if needed
- [ ] Followed commit message conventions
- [ ] Ensured all files are properly formatted

## Common Development Tasks

### Adding a New Process

1. Create process in `modules/` directory
2. Import and use in `workflows/`
3. Add tests for the process
4. Update documentation

### Modifying Parameters

1. Add parameter to `nextflow.config`
2. Update parameter validation in `main.nf`
3. Document in `docs/reference/parameters.md`
4. Add to test profiles if needed

### Adding New Dependencies

1. Update container definition (Docker/Singularity)
2. Test with both container engines
3. Document in requirements section

## Genomics-Specific Guidelines

### Data Handling
- Follow FAIR data principles (Findable, Accessible, Interoperable, Reusable)
- Respect privacy and ethical considerations for genomic data
- Use appropriate file formats (VCF, PLINK, BED, etc.)
- Consider scalability for large genomic datasets
- Never commit sensitive or private genomic data

### Algorithm Validation
- Validate changes against established benchmarks
- Document computational complexity
- Consider population diversity in testing
- Test with various genome builds (hg19, hg38, etc.)
- Verify chromosome naming compatibility

### Reproducibility
- Use version pinning for dependencies
- Provide containerized environments (Docker/Singularity)
- Document random seeds and parameters
- Include provenance tracking in outputs

## Review Process

1. **Automated checks**: CI/CD pipeline runs tests and style checks
2. **Code review**: Maintainers review technical implementation
3. **Testing**: Contributors and reviewers test with real data
4. **Documentation review**: Ensure clarity and completeness
5. **Approval**: At least one maintainer approval required

## Recognition

Contributors will be:
- Listed in the AUTHORS file
- Acknowledged in release notes
- Invited to co-author relevant publications
- Recognized in project presentations

## Communication

- **GitHub Discussions**: [AfriGen-D Discussions](https://github.com/orgs/AfriGen-D/discussions) - General questions and ideas
- **GitHub Issues**: [VCF Liftover Issues](https://github.com/AfriGen-D/vcf-liftover/issues) - Bug reports and feature requests
- **Helpdesk**: [helpdesk.afrigen-d.org](https://helpdesk.afrigen-d.org) - Private support inquiries
- **Email**: mamana.mbiyavanga@uct.ac.za - Direct contact with maintainers

## Resources

### Learning Resources
- [AfriGen-D Documentation](https://docs.afrigen-d.org)
- [VCF Liftover Documentation](https://afrigen-d.github.io/vcf-liftover)
- [nf-core Guidelines](https://nf-co.re/docs/contributing/guidelines)
- [Nextflow Documentation](https://www.nextflow.io/docs/latest/)

## Questions?

Don't hesitate to ask questions! You can:
- Open a discussion on [GitHub Discussions](https://github.com/orgs/AfriGen-D/discussions)
- Contact the maintainers directly
- Check the [FAQ in our documentation](https://afrigen-d.github.io/vcf-liftover/docs/)

Thank you for contributing to advancing African genomics research!

---

**AfriGen-D Development Team**
[afrigen-d.org](https://afrigen-d.org)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
