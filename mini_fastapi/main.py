from fastapi import FastAPI, File, Form, UploadFile
import io
from mini_fastapi.config import get_settings
from typing import List
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
import requests
from requests import Response
from PIL import Image
import namesgenerator

app = FastAPI()


@app.post("/files/")
async def create_file(
    file: UploadFile = File(default=None),
    label: str = Form(default=namesgenerator.get_random_name()),
    file_url: str = Form(default=None),
):

    if file is not None:
        image_data = file.file
    else:
        image_bytes = requests.get(file_url, stream=True).content
        image_data = io.BytesIO(image_bytes)
    settings = get_settings()
    computervision_client = ComputerVisionClient(
        settings.azure_cs_endpoint,
        CognitiveServicesCredentials(settings.azure_cs_api_key),
    )
    analysis_response = computervision_client.analyze_image_in_stream(
        image_data, [VisualFeatureTypes.tags]
    )
    return {
        "file_size": len(label),
        "fileb_content_type": file.content_type,
        "tags": [tag.name for tag in analysis_response.tags if tag.confidence > 0.5],
    }
