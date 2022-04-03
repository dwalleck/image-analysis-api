# Image Analysis API

## Usage

This project uses Azure Cognitive Services and Azure Blob Storage.
To properly run this application, you will need an Azure account
with a cogitive services and blob storage container named "images".
For the image URLs that are included in responses to be reachable,
anonymous access to the storage container must be enabled.


With a virtual environment enabled:

```
pip install -r requirements.txt
uvicorn image_analysis_api.api.main:app
```
