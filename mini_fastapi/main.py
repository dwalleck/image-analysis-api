import base64
from io import BytesIO
from typing import List
import uuid
from PIL import Image

import requests

from fastapi import FastAPI, HTTPException


from mini_fastapi.config import get_settings
from mini_fastapi.services.image_analysis_service import ImageAnalysisService
from mini_fastapi.services.image_storage_service import ImageStorageService
from mini_fastapi.models import AnalyzeImageRequest, AnalyzedImage
from mini_fastapi.data_access import database, images

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
    query = images.select().where(images.c.id == image_id)
    img = await database.fetch_one(query)
    if img is None:
        raise HTTPException(status_code=404, detail="Image not found")
    return img


@app.get("/images", response_model=List[AnalyzedImage] | List)
async def get_images(objects: str | None = None):
    if objects is None:
        query = images.select()
    else:
        query = images.select().where(images.c.objects.contains(objects.split(",")))
    images_from_db = await database.fetch_all(query)
    return images_from_db


@app.post("/images", response_model=AnalyzedImage)
async def upload_image(request: AnalyzeImageRequest):

    if request.image_data is not None:
        image_data = BytesIO(base64.b64decode(request.image_data))
    else:
        image_bytes = requests.get(request.image_url, stream=True).content
        image_data = BytesIO(image_bytes)

    settings = get_settings()

    if request.analyze_image:
        image_analysis_service = ImageAnalysisService(
            settings.azure_cs_endpoint, settings.azure_cs_api_key
        )
        objects = image_analysis_service.detect_objects(image_data)
    else:
        objects = []

    image_blob_name = get_image_name(image_data)
    image_service = ImageStorageService(settings.azure_storage_connection_string)
    url = image_service.upload_image(image_blob_name, image_data)

    query = images.insert().values(
        label=request.label,
        url=url,
        analyze_image=request.analyze_image,
        objects=objects,
    )
    image_id = await database.execute(query)

    return AnalyzedImage(id=image_id, label=request.label, objects=objects)


def get_image_name(image_data: BytesIO) -> str:
    image = Image.open(image_data)
    return f"image-{uuid.uuid4()}.{image.format.lower()}"
