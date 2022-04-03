from io import BytesIO
from azure.storage.blob import BlobServiceClient, BlobClient


class ImageStorageService:
    def __init__(self, connection_string: str) -> None:
        self.connection_string = connection_string

    def upload_image(self, image_name: str, image_data: BytesIO) -> str:
        blob_service_client = BlobServiceClient.from_connection_string(
            self.connection_string
        )
        blob_client: BlobClient = blob_service_client.get_blob_client(
            container="images", blob=image_name
        )
        blob_client.upload_blob(image_data)
        return blob_client.url
