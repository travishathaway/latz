import os
from pathlib import Path

#: Name of the application
APP_NAME = "latz"

#: Prefix used for environment variables
ENV_PREFIX = "LATZ_"

CONFIG_FILE_NAME = ".latz.json"

CONFIG_FILE_CWD = Path(os.getcwd()) / CONFIG_FILE_NAME

CONFIG_FILE_HOME_DIR = Path(os.path.expanduser("~")) / CONFIG_FILE_NAME

#: Config files to be loaded. Order will be respected, which means that
#: the config file on the bottom will override locations on the top.
CONFIG_FILES = (
    CONFIG_FILE_HOME_DIR,
    CONFIG_FILE_CWD,
)
