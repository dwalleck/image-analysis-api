import base64
import io
from typing import List
import uuid
from PIL import Image

import requests
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from fastapi import FastAPI, HTTPException
from msrest.authentication import CognitiveServicesCredentials
import uvicorn
from azure.storage.blob import BlobServiceClient, BlobClient


from mini_fastapi.config import get_settings
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
        image_data = io.BytesIO(base64.b64decode(request.image_data))
    else:
        image_bytes = requests.get(request.image_url, stream=True).content
        image_data = io.BytesIO(image_bytes)

    settings = get_settings()
    if request.analyze_image:
        computervision_client = ComputerVisionClient(
            settings.azure_cs_endpoint,
            CognitiveServicesCredentials(settings.azure_cs_api_key),
        )
        analysis_response = computervision_client.analyze_image_in_stream(
            image_data, [VisualFeatureTypes.objects]
        )

        objects = [
            obj.object_property
            for obj in analysis_response.objects
            if obj.confidence > 0.5
        ]
    else:
        objects = []

    img = Image.open(image_data)
    blob_service_client = BlobServiceClient.from_connection_string(
        settings.azure_storage_connection_string
    )
    image_blob_name = f"image-{uuid.uuid4()}.{img.format.lower()}"
    blob_client: BlobClient = blob_service_client.get_blob_client(
        container="images", blob=image_blob_name
    )
    blob_client.upload_blob(image_data)

    query = images.insert().values(
        label=request.label,
        url=blob_client.url,
        analyze_image=request.analyze_image,
        objects=objects,
    )
    image_id = await database.execute(query)

    return AnalyzedImage(id=image_id, label=request.label, objects=objects)
