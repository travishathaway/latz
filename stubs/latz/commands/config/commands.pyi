from ...config import ConfigError as ConfigError, parse_config_file_as_json as parse_config_file_as_json, write_config_file as write_config_file
from ...constants import CONFIG_FILE_CWD as CONFIG_FILE_CWD, CONFIG_FILE_HOME_DIR as CONFIG_FILE_HOME_DIR
from .validators import ConfigValuesValidator as ConfigValuesValidator
from _typeshed import Incomplete

validate_and_parse_config_values: Incomplete

def group() -> None: ...
def show_command(ctx) -> None: ...
def set_command(home, config_values) -> None: ...
