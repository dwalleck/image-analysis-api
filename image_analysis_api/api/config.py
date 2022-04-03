from functools import lru_cache
from pydantic import BaseSettings
from decimal import Decimal


class ImageAnalysisConfig(BaseSettings):
    azure_cs_api_key: str
    azure_cs_endpoint: str
    azure_cs_region: str
    azure_storage_connection_string: str
    postgres_connection_string: str
    acceptable_confidence_score: str

    class Config:
        env_file = ".env"


image_analysis_config = ImageAnalysisConfig()


@lru_cache()
def get_config() -> ImageAnalysisConfig:
    return image_analysis_config
