from pathlib import Path

from pydantic import BaseModel, ConfigDict, SecretStr


class BaseSettings(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, validate_assignment=True)


class Settings(BaseSettings):

    project_name: str
    env: str = "development"
    secret: SecretStr = "JDEkd3FLMERidi4kelpuQ2tWelFsM3NuVUdiZXFGUjltMQo="
    base_dir: Path
