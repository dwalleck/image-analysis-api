import uuid
from fastapi import HTTPException
from pydantic import BaseModel, Field, root_validator, validator

import io
from typing import List
from urllib.parse import urlparse
import namesgenerator


import requests
from fastapi import HTTPException
from PIL import Image

from image_analysis_api.api.validators import (
    image_has_allowed_content_type,
    image_is_allowable_dimensions,
    image_is_allowable_size,
    is_url_valid,
    allowed_image_types,
)


class AnalyzedImage(BaseModel):
    id: int
    label: str
    url: str
    objects: List[str]


class AnalyzeImageRequest(BaseModel):
    label: str = Field(
        default=namesgenerator.get_random_name(), min_length=1, max_length=50
    )
    analyze_image: bool = Field(default=False, title="If image analysis should be run")
    image_url: str | None = Field(default=None, title="URL of the image to analyze")
    image_data: str | None = Field(None, title="A base64 encoded image as a string")

    @root_validator
    def validate_image_url_or_base64_image_string(cls, values):
        if values.get("image_url") is None and values.get("image_data") is None:
            raise HTTPException(
                status_code=400,
                detail="Must provide one of image_url or image_data",
            )

        if (values.get("image_url") is not None) and (
            values.get("image_data") is not None
        ):
            raise HTTPException(
                status_code=400,
                detail="Cannot provide both image_url and image_data",
            )
        return values

    @validator("image_url")
    def validate_image_url(cls, v):
        image_url = v
        if image_url is None:
            return image_url

        if not is_url_valid(image_url):
            raise HTTPException(
                status_code=400, detail=f"{image_url} is an invalid URL"
            )
        try:
            response = requests.head(image_url)
            if not response.ok:
                raise HTTPException(
                    status_code=400, detail=f"{image_url} does not exist"
                )
        except requests.exceptions.RequestException:
            raise HTTPException(
                status_code=400,
                detail=f"An error occured accessing the image at {image_url}",
            )

        img_response = requests.get(image_url)
        image_bytes = img_response.content
        image_data = io.BytesIO(image_bytes)
        image = Image.open(image_data)
        if not image_is_allowable_dimensions(image):
            raise HTTPException(
                status_code=400,
                detail=f"{image_url} does not meet the minimum dimensions of 50 x 50",
            )

        content_type: str = response.headers["Content-Type"]
        if not image_has_allowed_content_type(content_type):
            raise HTTPException(
                status_code=400,
                detail=f"{content_type} is an invalid content type. Must be one of {allowed_image_types}",
            )

        if not image_is_allowable_size(len(image_bytes)):
            raise HTTPException(
                status_code=400, detail="Image must be smaller than 4 MB"
            )

        return v
