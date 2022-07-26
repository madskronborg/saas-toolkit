from typing import Optional, Type
from databases import Database
from pathlib import Path
from pydantic import BaseModel, SecretStr
from sqlalchemy import MetaData

from kitman.kits.iam.conf import IAMConfig
from kitman.plugins.redis import RedisConf
from deepmerge import always_merger
from kitman import errors

# App Settings
from kitman.kits.templating.apps import TemplatingConfig


class BaseSettings(BaseModel):
    class Config:
        arbitrary_types_allowed = True
        validate_assignment = True


class Settings(BaseSettings):

    project_name: str
    env: str = "development"
    secret: SecretStr = "JDEkd3FLMERidi4kelpuQ2tWelFsM3NuVUdiZXFGUjltMQo="
    base_dir: Path


settings: Settings = Settings()
