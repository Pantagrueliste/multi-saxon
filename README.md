# multi-saxon

[![DOI](https://zenodo.org/badge/680835550.svg)](https://zenodo.org/badge/latestdoi/680835550)

`multi-saxon` swiftly converts large amounts of XML TEI files into text. Harnessing the power of Saxonica's [SaxonC-HE](https://pypi.org/project/saxonche/) processor (XSLT 2.0+), it handles XSLT 2.0 and 3.0 transformations in parallel. This approach enables users to circumvent some of the limitations of `lxml`, which in spite of its speed, operates exclusively within the XSLT 1.0 framework.

## Features

- **Fast Transformations**: Utilize the multiprocessing capabilities of your machine for simultaneous XML transformations.
- **Memory Management**: Control batch sizes to optimize memory usage when processing large collections.
- **Saxon Integration**: Seamlessly process XML files using the renowned Saxon processor for XSLT 2.0+ support.
- **CSV Output**: Generate comprehensive CSV reports containing relevant metadata about the processed XML TEI files.
- **Extended Logging**: Detailed logging with configurable levels and formatted output.
- **Command-line Interface**: Easy-to-use CLI with support for various options and commands.
- **Flexible Configuration**: Configure via files, environment variables, or command-line options.
- **Automatic Retries**: Built-in retry mechanism for handling transient failures.
- **Language-Based Organization**: Output files organized by language extracted from TEI metadata.
- **Progress Tracking**: Visual progress bar showing processing status in real-time.

## Limitations

- `multi-saxon` is optimized for TEI P5 files. It is not intended for use with other XML frameworks.

## Installation

### From PyPI (Recommended)

```bash
pip install multi-saxon
```

### From Source

1. Ensure you have Python 3.7+ installed on your machine. If not, [download and install Python](https://www.python.org/downloads/).

2. Clone this repository:
   ```bash
   git clone https://github.com/Pantagrueliste/multi-saxon.git
   cd multi-saxon
   ```

3. Install the package:
   ```bash
   pip install -e .
   ```

## Quick Start

### Initialize Configuration

```bash
multi-saxon init
```

This creates a template configuration file (`config.toml`) that you can edit to customize settings.

### Validate Configuration

```bash
multi-saxon validate
```

Checks if your configuration is valid and warns about potential issues.

### Process XML Files

```bash
multi-saxon process
```

Processes XML files according to your configuration.

## Configuration

You can configure multi-saxon in three ways:

1. **Configuration File**: Edit the `config.toml` file
2. **Environment Variables**: Set variables like `MULTI_SAXON_INPUT_DIR`
3. **Command-line Options**: Pass options directly to the `process` command

### Example Configuration File

```toml
[input]
directory = "/path/to/xml/files"

[output]
directory = "/path/to/output"
metadata_file = "/path/to/output/metadata.csv"

[xslt]
file_path = "/path/to/transform.xsl"

[performance]
max_workers = 0  # 0 means use all CPU cores
batch_size = 100  # files per batch for memory optimization

[logging]
filename = "multi_saxon.log"
level = "INFO"
```

## Command-line Usage

```
Usage: multi-saxon [OPTIONS] COMMAND [ARGS]...

  multi-saxon: Parallel XML TEI to text transformer using Saxon

  A tool for efficiently processing large collections of XML TEI files using
  the Saxon XSLT processor and parallel processing.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  init       Initialize a new configuration file.
  process    Process XML files in parallel using Saxon.
  validate   Validate configuration file.
```

### Process Command Options

```
Usage: multi-saxon process [OPTIONS]

  Process XML files in parallel using Saxon.

  This command will transform XML files using the specified XSLT, extract
  metadata, and generate a CSV report.

Options:
  -c, --config FILE               Path to configuration file
  -i, --input-dir DIRECTORY       Directory containing XML files to process
  -o, --output-dir DIRECTORY      Directory to save output files
  -x, --xslt-file FILE            XSLT file to use for transformation
  -m, --metadata-file FILE        Path to save metadata CSV file
  -w, --workers INTEGER           Maximum number of worker processes (default:
                                  all CPU cores)
  -b, --batch-size INTEGER        Number of files to process in each batch
                                  (for memory optimization)
  -l, --log-file FILE             Path to log file (default: multi_saxon.log)
  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Log level (default: INFO)
  -v, --verbose                   Enable verbose output
  --help                          Show this message and exit.
```

## Advanced Usage

### Environment Variables

You can use these environment variables to configure multi-saxon:

- `MULTI_SAXON_INPUT_DIR`: Directory containing XML files
- `MULTI_SAXON_OUTPUT_DIR`: Directory to save output files
- `MULTI_SAXON_METADATA_FILE`: Path to save metadata CSV
- `MULTI_SAXON_XSLT_FILE`: XSLT file path
- `MULTI_SAXON_MAX_WORKERS`: Maximum worker processes
- `MULTI_SAXON_BATCH_SIZE`: Batch size for memory optimization
- `MULTI_SAXON_LOG_FILE`: Log file path
- `MULTI_SAXON_LOG_LEVEL`: Log level

### Memory Optimization

For very large collections, use the batch size option to control memory usage:

```bash
multi-saxon process --batch-size 50
```

This processes files in smaller batches to reduce peak memory consumption.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
