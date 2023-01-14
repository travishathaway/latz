from ..constants import ENV_PREFIX as ENV_PREFIX
from _typeshed import Incomplete
from pydantic import BaseSettings

class BaseAppConfig(BaseSettings):
    backend: str
    class Config:
        env_prefix: Incomplete
