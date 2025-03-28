"""
Utility modules for multi_saxon
"""

from multi_saxon.utils.config import Config, load_config
from multi_saxon.utils.file_utils import (
    ensure_dir_exists,
    count_words_in_file,
    get_file_extensions,
    get_file_size
)
from multi_saxon.utils.compatibility import upgrade_config, map_old_config_to_new