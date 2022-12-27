import os
from pathlib import Path

#: Name of the application
APP_NAME = "latz"

#: Prefix used for environment variables
ENV_PREFIX = "LATZ_"

#: Config files to be loaded. Order will be respected, which means that
#: the config file on the bottom will override locations on the top.
CONFIG_FILES = (
    Path(os.path.expanduser("~")) / ".latz.json",
    Path(os.getcwd()) / ".latz.json",
)
