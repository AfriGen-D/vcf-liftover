# Tutorials ​

Step-by-step tutorials to help you learn vcf-liftover effectively. These hands-on guides will take you from beginner to advanced user.

## Tutorial Overview ​

Our tutorials are designed to provide practical, hands-on experience with vcf-liftover. Each tutorial includes:

- **Clear objectives** - What you'll learn and accomplish
- **Prerequisites** - What you need before starting
- **Step-by-step instructions** - Detailed commands and explanations
- **Expected results** - What success looks like
- **Troubleshooting tips** - Common issues and solutions

## Available Tutorials ​

### Quick Start Tutorial (5 minutes) ​
**Perfect for:** First-time users who want to see results quickly

Learn the basics of running vcf-liftover with a simple example. This tutorial covers:
- Setting up your environment
- Running your first liftover
- Understanding basic output
- Interpreting success metrics

[Start Quick Start Tutorial →](/tutorials/quick-start)

### Multi-File Processing Tutorial (20 minutes) ​
**Perfect for:** Users who need to process multiple VCF files

Master batch processing with CSV input files. This tutorial covers:
- Preparing CSV input files
- Configuring multi-file processing
- Managing large datasets
- Monitoring progress and results

[Start Multi-File Tutorial →](/tutorials/multi-file-tutorial)

### Method Selection Tutorial (15 minutes) ​
**Perfect for:** Users who want to understand different processing options

Learn how to choose the right parameters for your data. This tutorial covers:
- Understanding liftover parameters
- Choosing appropriate validation settings
- Optimizing for different data types
- Performance considerations

[Start Method Selection Tutorial →](/tutorials/method-selection)

## Tutorial Difficulty Levels ​

### 🟢 Beginner
- Quick Start Tutorial
- Basic concepts and commands
- Minimal prerequisites

### 🟡 Intermediate  
- Multi-File Processing Tutorial
- Method Selection Tutorial
- Some command-line experience helpful

### 🔴 Advanced
- Custom configuration tutorials
- Performance optimization
- Integration with other tools

## Before You Start ​

### Prerequisites for All Tutorials ​

- Nextflow installed (≥ 22.10.1)
- Docker or Singularity available
- Basic command-line familiarity
- Access to test data (provided in tutorials)

### Setting Up Your Environment ​

```bash
# Clone the repository
git clone https://github.com/AfriGen-D/vcf-liftover.git
cd vcf-liftover

# Verify Nextflow installation
nextflow -version

# Check container engine
singularity --version
# OR
docker --version
```

## Tutorial Learning Path ​

We recommend following this learning path:

1. **Start Here:** [Quick Start Tutorial](/tutorials/quick-start)
   - Get familiar with basic concepts
   - Run your first successful liftover

2. **Next:** [Multi-File Processing](/tutorials/multi-file-tutorial)
   - Learn batch processing
   - Handle real-world datasets

3. **Advanced:** [Method Selection](/tutorials/method-selection)
   - Optimize for your specific needs
   - Understand parameter choices

## Getting Help ​

If you get stuck during any tutorial:

1. **Check the troubleshooting section** in each tutorial
2. **Review the [Documentation](/docs/)** for detailed explanations
3. **Search [GitHub Issues](https://github.com/AfriGen-D/vcf-liftover/issues)**
4. **Ask for help** on our support channels

## Tutorial Feedback ​

Help us improve these tutorials:

- Report issues or unclear instructions
- Suggest new tutorial topics
- Share your success stories
- Contribute improvements via GitHub

## What's Next? ​

After completing the tutorials:

- Explore the [Documentation](/docs/) for comprehensive reference material
- Check out [Examples](/examples/) for real-world use cases
- Review the [Reference](/reference/) for complete parameter documentation
- Join the AfriGen-D community for ongoing support

Ready to start learning? Begin with our [Quick Start Tutorial](/tutorials/quick-start)!
