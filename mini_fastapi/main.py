import base64
from email.mime import image
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
from mini_fastapi.models import AnalyzeImageRequest
from mini_fastapi.data_access import database, images

app = FastAPI()


# @app.on_event("startup")
# async def startup():
#     await database.connect()


# @app.on_event("shutdown")
# async def shutdown():
#     await database.disconnect()


# @app.get("/images", response_model=List[AnalyzedImage])
# async def get_images():
#     query = images.select()
#     images_from_db = await database.fetch_all(query)
#     return images_from_db


@app.post("/images")
async def upload_image(request: AnalyzeImageRequest):

    if request.base64_image_string is not None:
        image_data = io.BytesIO(base64.b64decode(request.base64_image_string))
    else:
        image_bytes = requests.get(request.image_url, stream=True).content
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
        "label": request.label,
        "tags": [tag.name for tag in analysis_response.tags if tag.confidence > 0.5],
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
