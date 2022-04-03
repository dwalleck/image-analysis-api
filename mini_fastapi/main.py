import base64
from decimal import Decimal
from io import BytesIO
from typing import List
import uuid
from PIL import Image

import requests

from fastapi import Depends, FastAPI, HTTPException


from mini_fastapi.config import ImageAnalysisConfig, get_config
from mini_fastapi.images_repo import ImageRepository
from mini_fastapi.services.image_analysis_service import ImageAnalysisService
from mini_fastapi.services.image_storage_service import ImageStorageService
from mini_fastapi.models import AnalyzeImageRequest, AnalyzedImage
from mini_fastapi.db import database, images

app = FastAPI(
    title="Image Analysis API", description="Image Analysis API", version="1.0.0"
)


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/images/{image_id}", response_model=AnalyzedImage)
async def get_image_by_id(image_id: int):
    image_repo = ImageRepository(images, database)
    img = await image_repo.get_image(image_id)
    if img is None:
        raise HTTPException(status_code=404, detail="Image not found")
    return img


@app.get("/images", response_model=List[AnalyzedImage] | List)
async def get_images(objects: str | None = None):
    image_repo = ImageRepository(images, database)
    images_from_db = await image_repo.get_images(objects)
    return images_from_db


@app.post("/images", response_model=AnalyzedImage)
async def analyze_image(
    request: AnalyzeImageRequest, config: ImageAnalysisConfig = Depends(get_config)
):
    if request.image_data is not None:
        image_data = BytesIO(base64.b64decode(request.image_data))
    else:
        image_bytes = requests.get(request.image_url, stream=True).content
        image_data = BytesIO(image_bytes)

    if request.analyze_image:
        image_analysis_service = ImageAnalysisService(
            config.azure_cs_endpoint, config.azure_cs_api_key
        )

        objects = image_analysis_service.detect_objects(
            image_data, Decimal(config.acceptable_confidence_score)
        )
    else:
        objects = []

    image_blob_name = get_image_name(image_data)
    image_service = ImageStorageService(config.azure_storage_connection_string)
    url = image_service.upload_image(image_blob_name, image_data)

    image_repo = ImageRepository(images, database)
    image_id = await image_repo.create_image(
        request.label, url, request.analyze_image, objects
    )

    return AnalyzedImage(id=image_id, label=request.label, objects=objects, url=url)


def get_image_name(image_data: BytesIO) -> str:
    image = Image.open(image_data)
    return f"image-{uuid.uuid4()}.{image.format.lower()}"
