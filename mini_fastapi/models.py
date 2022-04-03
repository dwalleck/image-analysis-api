from fastapi import HTTPException
from pydantic import BaseModel, root_validator, validator

import io
from typing import List
from urllib.parse import urlparse

import requests
from fastapi import HTTPException
from PIL import Image

from mini_fastapi.validators import (
    image_has_allowed_content_type,
    image_is_allowable_dimensions,
    image_is_allowable_size,
    is_url_valid,
    allowed_image_types,
)


class AnalyzeImageRequest(BaseModel):
    label: str | None = None
    run_image_analysis: bool | None = False
    image_url: str | None = None
    base64_image_string: str | None = None

    @root_validator
    def validate_image_url_or_base64_image_string(cls, values):
        if (
            values.get("image_url") is None
            and values.get("base64_image_string") is None
        ):
            raise HTTPException(
                status_code=400,
                detail="Must provide one of image_url or base64_image_string",
            )

        if (values.get("image_url") is not None) and (
            values.get("base64_image_string") is not None
        ):
            raise HTTPException(
                status_code=400,
                detail="Cannot provide both image_url and base64_image_string",
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

        img_response = requests.get(image_url, stream=True)
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

        if not image_is_allowable_size(int(response.headers.get("content-length"))):
            raise HTTPException(
                status_code=400, detail="Image must be smaller than 4 MB"
            )

        return v
