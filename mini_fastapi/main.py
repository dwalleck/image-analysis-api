import io
from typing import List

import namesgenerator
import requests
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from msrest.authentication import CognitiveServicesCredentials
import uvicorn

from mini_fastapi.config import get_settings
from mini_fastapi.validators import validate_image_file, validate_image_url

app = FastAPI()


@app.post("/files/")
async def create_file(
    file: UploadFile = File(default=None),
    label: str = Form(default=namesgenerator.get_random_name()),
    file_url: str = Form(default=None),
):
    if file and file_url:
        raise HTTPException(
            status_code=400, detail="Please provide either a file or a url"
        )

    if file is not None:
        validate_image_file(file)
        image_data = file.file
    # else:
    #     validate_image_url(file_url)
    #     image_bytes = requests.get(file_url, stream=True).content
    #     image_data = io.BytesIO(image_bytes)
    # settings = get_settings()
    # computervision_client = ComputerVisionClient(
    #     settings.azure_cs_endpoint,
    #     CognitiveServicesCredentials(settings.azure_cs_api_key),
    # )
    # analysis_response = computervision_client.analyze_image_in_stream(
    #     image_data, [VisualFeatureTypes.tags]
    # )
    return {
        "file_size": len(file.file.read()),
        "fileb_content_type": file.content_type,
        # "tags": [tag.name for tag in analysis_response.tags if tag.confidence > 0.5],
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
