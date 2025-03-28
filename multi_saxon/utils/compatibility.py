"""
Compatibility utilities for backward compatibility with older versions
"""

import os
import toml
from typing import Dict, Any


def upgrade_config(old_config_path: str, new_config_path: str) -> None:
    """
    Upgrade an old format config.toml to the new format
    
    Args:
        old_config_path: Path to the old config file
        new_config_path: Path to save the new config file
    """
    try:
        # Load the old config
        old_config = toml.load(old_config_path)
        
        # Create the new config structure
        new_config = {
            "input": {
                "directory": old_config.get("input", {}).get("directory", "")
            },
            "output": {
                "directory": old_config.get("output", {}).get("directory", ""),
                "metadata_file": old_config.get("output", {}).get("metadata_file", "")
            },
            "xslt": {
                "file_path": old_config.get("xslt", {}).get("file_path", "")
            },
            "performance": {
                "max_workers": 0,  # Default to using all cores
                "batch_size": 100  # Default batch size
            },
            "logging": {
                "filename": old_config.get("logging", {}).get("filename", "multi_saxon.log"),
                "level": "INFO"  # Default to INFO level
            }
        }
        
        # Write the new config
        with open(new_config_path, "w") as f:
            toml.dump(new_config, f)
            
    except Exception as e:
        raise ValueError(f"Failed to upgrade configuration: {e}")


def map_old_config_to_new(old_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map old config structure to new structure in memory
    
    Args:
        old_config: Old configuration dictionary
        
    Returns:
        New configuration dictionary
    """
    # Create the new config structure
    new_config = {
        "input": {
            "directory": old_config.get("input", {}).get("directory", "")
        },
        "output": {
            "directory": old_config.get("output", {}).get("directory", ""),
            "metadata_file": old_config.get("output", {}).get("metadata_file", "")
        },
        "xslt": {
            "file_path": old_config.get("xslt", {}).get("file_path", "")
        },
        "performance": {
            "max_workers": 0,  # Default to using all cores
            "batch_size": None  # No batching by default
        },
        "logging": {
            "filename": old_config.get("logging", {}).get("filename", "multi_saxon.log"),
            "level": "INFO"  # Default to INFO level
        }
    }
    
    return new_config