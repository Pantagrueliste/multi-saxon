"""
Command-line interface for multi_saxon
"""

import os
import sys
import click
import logging
from typing import Optional

from multi_saxon import __version__
from multi_saxon.utils import load_config
from multi_saxon.core import SaxonProcessor


@click.group()
@click.version_option(__version__, prog_name="multi-saxon")
def cli():
    """
    multi-saxon: Parallel XML TEI to text transformer using Saxon
    
    A tool for efficiently processing large collections of XML TEI files
    using the Saxon XSLT processor and parallel processing.
    """
    pass


@cli.command()
@click.option(
    "--config", "-c",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    help="Path to configuration file"
)
@click.option(
    "--input-dir", "-i",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True),
    envvar="MULTI_SAXON_INPUT_DIR",
    help="Directory containing XML files to process"
)
@click.option(
    "--output-dir", "-o",
    type=click.Path(file_okay=False, dir_okay=True, writable=True),
    envvar="MULTI_SAXON_OUTPUT_DIR",
    help="Directory to save output files"
)
@click.option(
    "--xslt-file", "-x",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    envvar="MULTI_SAXON_XSLT_FILE",
    help="XSLT file to use for transformation"
)
@click.option(
    "--metadata-file", "-m",
    type=click.Path(file_okay=True, dir_okay=False, writable=True),
    envvar="MULTI_SAXON_METADATA_FILE",
    help="Path to save metadata CSV file"
)
@click.option(
    "--workers", "-w",
    type=int,
    envvar="MULTI_SAXON_MAX_WORKERS",
    help="Maximum number of worker processes (default: all CPU cores)"
)
@click.option(
    "--batch-size", "-b",
    type=int,
    envvar="MULTI_SAXON_BATCH_SIZE",
    help="Number of files to process in each batch (for memory optimization)"
)
@click.option(
    "--log-file", "-l",
    type=click.Path(file_okay=True, dir_okay=False, writable=True),
    envvar="MULTI_SAXON_LOG_FILE",
    default="multi_saxon.log",
    help="Path to log file (default: multi_saxon.log)"
)
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False),
    envvar="MULTI_SAXON_LOG_LEVEL",
    default="INFO",
    help="Log level (default: INFO)"
)
@click.option(
    "--verbose", "-v",
    is_flag=True,
    help="Enable verbose output"
)
def process(
    config: Optional[str] = None,
    input_dir: Optional[str] = None,
    output_dir: Optional[str] = None,
    xslt_file: Optional[str] = None,
    metadata_file: Optional[str] = None,
    workers: Optional[int] = None,
    batch_size: Optional[int] = None,
    log_file: str = "multi_saxon.log",
    log_level: str = "INFO",
    verbose: bool = False
):
    """
    Process XML files in parallel using Saxon.
    
    This command will transform XML files using the specified XSLT,
    extract metadata, and generate a CSV report.
    """
    try:
        # Set up command-line logging
        if verbose:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_formatter = logging.Formatter('%(levelname)s: %(message)s')
            console_handler.setFormatter(console_formatter)
            logging.getLogger().addHandler(console_handler)
        
        # Load configuration, with command-line options taking precedence
        config_obj = load_config(config)
        
        # Override config with command-line options if provided
        if input_dir:
            config_obj.input_directory = input_dir
        if output_dir:
            config_obj.output_directory = output_dir
        if xslt_file:
            config_obj.xslt_file_path = xslt_file
        if metadata_file:
            config_obj.metadata_file = metadata_file
        if workers is not None:
            config_obj.max_workers = workers
        if batch_size is not None:
            config_obj.batch_size = batch_size
        if log_file:
            config_obj.log_file = log_file
        if log_level:
            config_obj.log_level = log_level
        
        # Initialize processor and run
        processor = SaxonProcessor(config_obj)
        processor.process_all(batch_size=config_obj.batch_size)
        
    except ValueError as e:
        click.echo(f"Configuration error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        if verbose:
            import traceback
            click.echo(traceback.format_exc(), err=True)
        sys.exit(1)


@cli.command()
@click.option(
    "--output", "-o",
    type=click.Path(file_okay=True, dir_okay=False, writable=True),
    default="config.toml",
    help="Path to save the generated configuration file"
)
@click.option(
    "--force", "-f",
    is_flag=True,
    help="Overwrite existing configuration file"
)
def init(output: str = "config.toml", force: bool = False):
    """
    Initialize a new configuration file.
    
    This command creates a template configuration file that you can
    customize for your project.
    """
    if os.path.exists(output) and not force:
        click.echo(f"Error: {output} already exists. Use --force to overwrite.", err=True)
        sys.exit(1)
    
    config_template = """# multi-saxon configuration file

[input]
directory = "/path/to/xml/files"  # Directory containing XML files to process

[output]
directory = "/path/to/output"     # Directory to save converted text files
metadata_file = "/path/to/output/metadata.csv"  # Path to save metadata CSV file

[xslt]
file_path = "/path/to/transform.xsl"  # XSLT file to use for transformation

[performance]
max_workers = 0  # Maximum number of worker processes (0 = use all CPU cores)
batch_size = 100  # Number of files to process in each batch (for memory optimization)

[logging]
filename = "multi_saxon.log"  # Log file path
level = "INFO"  # Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
"""
    
    try:
        with open(output, "w") as f:
            f.write(config_template)
        click.echo(f"Configuration template created at {output}")
        click.echo("Please edit this file to customize settings for your project.")
    except Exception as e:
        click.echo(f"Error creating configuration file: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option(
    "--config", "-c",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    help="Path to configuration file to validate"
)
def validate(config: Optional[str] = None):
    """
    Validate configuration file.
    
    This command checks if the configuration file is valid and all
    required settings are present.
    """
    try:
        # Attempt to load the configuration
        if not config:
            config = "config.toml"
            if not os.path.exists(config):
                click.echo(f"Error: Default configuration file {config} not found.", err=True)
                sys.exit(1)
        
        config_obj = load_config(config)
        
        # Check if required paths exist
        warnings = []
        
        if not os.path.isdir(config_obj.input_directory):
            warnings.append(f"Warning: Input directory does not exist: {config_obj.input_directory}")
        
        if not os.path.isfile(config_obj.xslt_file_path):
            warnings.append(f"Warning: XSLT file does not exist: {config_obj.xslt_file_path}")
        
        # Output directory will be created if it doesn't exist, but parent dir should exist
        output_parent = os.path.dirname(config_obj.output_directory)
        if output_parent and not os.path.isdir(output_parent):
            warnings.append(f"Warning: Output directory parent does not exist: {output_parent}")
        
        # Metadata file parent directory should exist
        metadata_parent = os.path.dirname(config_obj.metadata_file)
        if metadata_parent and not os.path.isdir(metadata_parent):
            warnings.append(f"Warning: Metadata file parent directory does not exist: {metadata_parent}")
        
        # Print validation result
        if warnings:
            click.echo("Configuration is valid but with warnings:")
            for warning in warnings:
                click.echo(warning)
        else:
            click.echo("Configuration is valid!")
            
        # Print configuration summary
        click.echo("\nConfiguration summary:")
        click.echo(f"  Input directory: {config_obj.input_directory}")
        click.echo(f"  Output directory: {config_obj.output_directory}")
        click.echo(f"  Metadata file: {config_obj.metadata_file}")
        click.echo(f"  XSLT file: {config_obj.xslt_file_path}")
        click.echo(f"  Max workers: {config_obj.max_workers or 'all available'}")
        click.echo(f"  Batch size: {config_obj.batch_size or 'none (divide equally)'}")
        click.echo(f"  Log file: {config_obj.log_file}")
        click.echo(f"  Log level: {config_obj.log_level}")
        
    except ValueError as e:
        click.echo(f"Configuration error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option(
    "--input", "-i",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    default="config.toml",
    help="Path to old configuration file"
)
@click.option(
    "--output", "-o",
    type=click.Path(file_okay=True, dir_okay=False, writable=True),
    default="config.new.toml",
    help="Path to save upgraded configuration file"
)
@click.option(
    "--force", "-f",
    is_flag=True,
    help="Overwrite existing output file"
)
def upgrade_config(input: str = "config.toml", output: str = "config.new.toml", force: bool = False):
    """
    Upgrade a configuration file from old to new format.
    
    This command converts an old format configuration file to the new format
    with additional options for performance tuning and logging.
    """
    from multi_saxon.utils.compatibility import upgrade_config as upgrade_func
    
    if os.path.exists(output) and not force:
        click.echo(f"Error: Output file {output} already exists. Use --force to overwrite.", err=True)
        sys.exit(1)
    
    try:
        upgrade_func(input, output)
        click.echo(f"Configuration file upgraded successfully: {output}")
        click.echo("You can now use this new configuration file with multi-saxon.")
    except ValueError as e:
        click.echo(f"Error upgrading configuration: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()