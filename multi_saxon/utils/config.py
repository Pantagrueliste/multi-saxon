"""
Configuration management for multi_saxon
"""

import os
import toml
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class Config:
    """Configuration class for multi_saxon"""
    
    # Input/output settings
    input_directory: str
    output_directory: str
    metadata_file: str
    xslt_file_path: str
    
    # Performance settings
    max_workers: int = 0  # 0 means use all available cores
    batch_size: Optional[int] = None
    
    # Logging settings
    log_file: str = "multi_saxon.log"
    log_level: str = "INFO"
    
    @classmethod
    def from_file(cls, config_file: str) -> 'Config':
        """
        Load configuration from a TOML file
        
        Args:
            config_file: Path to the configuration file
            
        Returns:
            Config object with values from the file
        """
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
        try:
            config_data = toml.load(config_file)
            
            # Required settings
            input_directory = config_data.get("input", {}).get("directory")
            output_directory = config_data.get("output", {}).get("directory")
            metadata_file = config_data.get("output", {}).get("metadata_file")
            xslt_file_path = config_data.get("xslt", {}).get("file_path")
            
            # Validate required settings
            if not all([input_directory, output_directory, metadata_file, xslt_file_path]):
                missing = []
                if not input_directory: missing.append("input.directory")
                if not output_directory: missing.append("output.directory")
                if not metadata_file: missing.append("output.metadata_file")
                if not xslt_file_path: missing.append("xslt.file_path")
                
                raise ValueError(f"Missing required configuration: {', '.join(missing)}")
            
            # Optional settings with defaults
            max_workers = config_data.get("performance", {}).get("max_workers", 0)
            batch_size = config_data.get("performance", {}).get("batch_size")
            log_file = config_data.get("logging", {}).get("filename", "multi_saxon.log")
            log_level = config_data.get("logging", {}).get("level", "INFO")
            
            return cls(
                input_directory=input_directory,
                output_directory=output_directory,
                metadata_file=metadata_file,
                xslt_file_path=xslt_file_path,
                max_workers=max_workers,
                batch_size=batch_size,
                log_file=log_file,
                log_level=log_level
            )
            
        except Exception as e:
            raise ValueError(f"Error parsing configuration file: {e}")
    
    @classmethod
    def from_env(cls) -> 'Config':
        """
        Load configuration from environment variables
        
        Returns:
            Config object with values from environment variables
        """
        # Required settings
        input_directory = os.environ.get("MULTI_SAXON_INPUT_DIR")
        output_directory = os.environ.get("MULTI_SAXON_OUTPUT_DIR")
        metadata_file = os.environ.get("MULTI_SAXON_METADATA_FILE")
        xslt_file_path = os.environ.get("MULTI_SAXON_XSLT_FILE")
        
        # Validate required settings
        if not all([input_directory, output_directory, metadata_file, xslt_file_path]):
            missing = []
            if not input_directory: missing.append("MULTI_SAXON_INPUT_DIR")
            if not output_directory: missing.append("MULTI_SAXON_OUTPUT_DIR")
            if not metadata_file: missing.append("MULTI_SAXON_METADATA_FILE")
            if not xslt_file_path: missing.append("MULTI_SAXON_XSLT_FILE")
            
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        # Optional settings with defaults
        max_workers = int(os.environ.get("MULTI_SAXON_MAX_WORKERS", "0"))
        batch_size_str = os.environ.get("MULTI_SAXON_BATCH_SIZE")
        batch_size = int(batch_size_str) if batch_size_str else None
        log_file = os.environ.get("MULTI_SAXON_LOG_FILE", "multi_saxon.log")
        log_level = os.environ.get("MULTI_SAXON_LOG_LEVEL", "INFO")
        
        return cls(
            input_directory=input_directory,
            output_directory=output_directory,
            metadata_file=metadata_file,
            xslt_file_path=xslt_file_path,
            max_workers=max_workers,
            batch_size=batch_size,
            log_file=log_file,
            log_level=log_level
        )


def load_config(config_file: Optional[str] = None) -> Config:
    """
    Load configuration from file or environment variables
    
    Args:
        config_file: Optional path to configuration file
        
    Returns:
        Config object with loaded configuration
        
    Raises:
        ValueError: If configuration cannot be loaded
    """
    # Try loading from file first if provided
    if config_file:
        try:
            return Config.from_file(config_file)
        except Exception as e:
            raise ValueError(f"Failed to load configuration from file: {e}")
    
    # Then try environment variables
    try:
        return Config.from_env()
    except ValueError:
        # If environment variables are not set and no file was provided, try default locations
        default_locations = ["./config.toml", "~/.config/multi_saxon/config.toml"]
        
        for location in default_locations:
            expanded_path = os.path.expanduser(location)
            if os.path.exists(expanded_path):
                try:
                    return Config.from_file(expanded_path)
                except Exception:
                    # Continue to the next location if this one fails
                    continue
        
        # If we get here, we couldn't load configuration from anywhere
        raise ValueError(
            "Could not load configuration. Please provide a configuration file or set environment variables."
        )