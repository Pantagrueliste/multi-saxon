#!/usr/bin/env python3
"""
Legacy entry point for multi-saxon

This script provides backward compatibility with the original multi-saxon.py
It imports and runs the new modular version from the package.
"""

import os
import sys
import warnings

warnings.warn(
    "Using legacy entry point (multi-saxon.py) is deprecated. "
    "Please install and use the new command-line interface: "
    "`pip install -e .` and then use `multi-saxon process`",
    DeprecationWarning,
    stacklevel=2
)

# Add the package directory to the path
package_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, package_dir)

try:
    from multi_saxon.cli.main import process as process_command
    from multi_saxon.utils import load_config
    
    # Run the main process command with the default config
    process_command(verbose=True)
    
except ImportError:
    print("Error: Could not import the multi-saxon package.")
    print("Please install it using: pip install -e multi_saxon")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
