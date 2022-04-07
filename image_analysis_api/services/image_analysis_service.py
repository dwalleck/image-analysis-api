from decimal import Decimal
from io import BytesIO
from typing import List

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials


class ImageAnalysisService:
    def __init__(self, endpoint: str, api_key: str) -> None:
        self.endpoint = endpoint
        self.api_key = api_key

    def detect_objects(
        self, image_data: bytes, acceptable_confidence_score: Decimal
    ) -> List[str]:
        computervision_client = ComputerVisionClient(
            endpoint=self.endpoint,
            credentials=CognitiveServicesCredentials(self.api_key),
        )
        analysis_response = computervision_client.analyze_image_in_stream(
            BytesIO(image_data), [VisualFeatureTypes.objects]
        )

        objects = [
            obj.object_property
            for obj in analysis_response.objects
            if Decimal(obj.confidence) > acceptable_confidence_score
        ]
        return objects
