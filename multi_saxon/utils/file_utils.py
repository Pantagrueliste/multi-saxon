"""
File utility functions for multi_saxon
"""

import os
from typing import List, Dict, Any, Optional


def ensure_dir_exists(directory: str) -> None:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory: Directory path to ensure exists
    """
    if not directory:
        return
        
    os.makedirs(directory, exist_ok=True)


def count_words_in_file(file_path: str) -> int:
    """
    Count the number of words in a file.
    
    Args:
        file_path: Path to the file to count words in
        
    Returns:
        Number of words in the file
    """
    with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
        text = file.read()
    return len(text.split())


def get_file_extensions(directory: str) -> Dict[str, int]:
    """
    Get a count of file extensions in a directory (recursive).
    
    Args:
        directory: Directory to scan
        
    Returns:
        Dictionary mapping file extensions to counts
    """
    extensions = {}
    
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            _, ext = os.path.splitext(filename)
            if ext:
                # Remove the dot and lowercase
                ext = ext[1:].lower()
                extensions[ext] = extensions.get(ext, 0) + 1
    
    return extensions


def get_file_size(file_path: str) -> int:
    """
    Get file size in bytes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File size in bytes
    """
    try:
        return os.path.getsize(file_path)
    except (FileNotFoundError, OSError):
        return 0