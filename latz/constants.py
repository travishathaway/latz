import os
from pathlib import Path

#: Name of the application
APP_NAME = "latz"

#: Prefix used for environment variables
ENV_PREFIX = "LATZ_"

CONFIG_FILE_NAME = ".latz.json"

#: Config files to be loaded. Order will be respected, which means that
#: the config file on the bottom will override locations on the top.
CONFIG_FILES = (
    Path(os.path.expanduser("~")) / CONFIG_FILE_NAME,
    Path(os.getcwd()) / CONFIG_FILE_NAME,
)
