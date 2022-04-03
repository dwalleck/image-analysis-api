from functools import lru_cache
from pydantic import BaseSettings


class Settings(BaseSettings):
    azure_cs_api_key: str
    azure_cs_endpoint: str
    azure_cs_region: str
    azure_storage_connection_string: str

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
