from pydantic import BaseSettings, Field

from ..constants import ENV_PREFIX


class BaseAppConfig(BaseSettings):
    """
    Holds all settings for the latz application. These are parsed from
    config files, command line arguments and environment variables.
    """

    backend: str = Field(
        default="unsplash",
        description="Image search backend to use for retrieving images.",
    )

    class Config:
        env_prefix = ENV_PREFIX
