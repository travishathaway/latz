from pathlib import Path
from collections.abc import Sequence

from pydantic import ValidationError

#: Suggestion for where to find a documentation on configuration parameters
PARSE_ERROR_SUGGESTION = ""  # TODO: link to documentation

CONFIG_ERROR_PREFIX = "Unable to parse configuration file"


def format_validation_error(exc: ValidationError, path: Path) -> str:
    """
    Formats a ``pydantic.Validation`` error as a ``str``
    """
    error_str = []
    for err in exc.errors():
        loc = ",".join(err.get("loc", tuple()))  # type: ignore
        ctx = err.get("ctx", {})
        given = ctx.get("given")
        permitted = ctx.get("permitted")
        msg = err.get("msg")

        # Add strings
        error_str.append(f"\n  {loc}: \n")
        error_str.append(f"    {msg}\n")

        if given and permitted:
            error_str.append("  provided_value: ")
            error_str.append(f"'{given}'\n")

    return "".join(
        (f"{CONFIG_ERROR_PREFIX}: {path}\n", *error_str),
    )


def format_all_validation_errors(validation_errors: Sequence[str]) -> str:
    """
    Formats a sequence of errors as a single ``str``
    """
    error_str = "\n\n".join(validation_errors)
    # error_str += f"\n\n{PARSE_ERROR_SUGGESTION}"  #TODO: uncomment when no long blank string

    return error_str
