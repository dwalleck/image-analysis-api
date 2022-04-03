from typing import List
from urllib.parse import urlparse

from PIL import Image

"""
Image Analysis works on:
- JPEG, PNG, GIF, or BMP format
- The file size of the image must be less than 4 megabytes (MB)
- The dimensions of the image must be greater than 50 x 50 pixels
"""

allowed_image_types: List[str] = ["image/jpeg", "image/png", "image/gif", "image/bmp"]

# Stack Overflow: https://stackoverflow.com/questions/14906764/how-to-check-if-image-is-a-gif-using-python
def is_url_valid(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        # TODO: This should be an exception
        return False


def image_is_allowable_dimensions(image: Image) -> bool:
    width, height = image.size
    print(f"Image dimensions: {width} x {height}")
    return width > 50 and height > 50


def image_has_allowed_content_type(content_type: str) -> bool:
    return content_type in allowed_image_types


def image_is_allowable_size(image_size) -> bool:
    return image_size < 1024 * 1024 * 4


# def validate_image_file(image_file: UploadFile) -> bool:

#     if not image_has_allowed_content_type(image_file.content_type):
#         raise HTTPException(
#             status_code=400,
#             detail=f"{image_file.content_type} is an invalid content type. Must be one of {allowed_image_types}",
#         )

#     # if not image_is_allowable_size(len(image_file.file.read())):
#     #     raise HTTPException(status_code=400, detail="Image must be smaller than 4 MB")

#     if not image_is_allowable_dimensions(Image.open(image_file.file)):
#         raise HTTPException(
#             status_code=400,
#             detail=f"{image_file.filename} does not meet the minimum dimensions of 50 x 50",
#         )
#     return True


# def validate_image_url(image_url: str) -> bool:
#     if not is_url_valid(image_url):
#         raise HTTPException(status_code=400, detail=f"{image_url} is an invalid URL")

#     try:
#         response = requests.head(image_url)
#         if not response.ok:
#             raise HTTPException(status_code=400, detail=f"{image_url} does not exist")
#     except requests.exceptions.RequestException:
#         raise HTTPException(
#             status_code=400,
#             detail=f"An error occured accessing the image at {image_url}",
#         )

#     img_response = requests.get(image_url, stream=True)
#     image_bytes = img_response.content
#     image_data = io.BytesIO(image_bytes)
#     image = Image.open(image_data)

#     if not image_is_allowable_dimensions(image):
#         raise HTTPException(
#             status_code=400,
#             detail=f"{image_url} does not meet the minimum dimensions of 50 x 50",
#         )

#     content_type: str = response.headers["Content-Type"]
#     if not image_has_allowed_content_type(content_type):
#         raise HTTPException(
#             status_code=400,
#             detail=f"{content_type} is an invalid content type. Must be one of {allowed_image_types}",
#         )

#     if not image_is_allowable_size(int(response.headers.get("content-length"))):
#         raise HTTPException(status_code=400, detail="Image must be smaller than 4 MB")

#     return True
