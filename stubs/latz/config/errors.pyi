from collections.abc import Sequence
from pathlib import Path
from pydantic import ValidationError as ValidationError

PARSE_ERROR_SUGGESTION: str
CONFIG_ERROR_PREFIX: str

def format_validation_error(exc: ValidationError, path: Path) -> str: ...
def format_all_validation_errors(validation_errors: Sequence[str]) -> str: ...
