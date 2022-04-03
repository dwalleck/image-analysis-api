from wsgiref.validate import validator
from fastapi import HTTPException
from pydantic import BaseModel, root_validator


class AnalyzeImageRequest(BaseModel):
    label: str | None = None
    image_url: str | None = None
    base64_image_string: str | None = None

    @root_validator
    def validate_image_url_or_base64_image_string(cls, values):
        if (
            values.get("image_url") is None
            and values.get("base64_image_string") is None
        ):
            raise ValueError(
                "Must provide one of image_url or base64_image_string",
            )

        if (values.get("image_url") is not None) and (
            values.get("base64_image_string") is not None
        ):
            raise ValueError("Must provide one of image_url or base64_image_string")
        return values

    @validator("base64_image_string")
    def validate_base64_image_string(cls, v):
        if v is not None:
            if not isinstance(v, str):
                raise ValueError("base64_image_string must be a string")
        return v
