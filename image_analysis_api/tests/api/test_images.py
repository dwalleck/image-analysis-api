import base64
import os
from fastapi import HTTPException

from fastapi.testclient import TestClient
import pytest

from image_analysis_api.api.main import analyze_image, app


@pytest.fixture
def encoded_image_string():
    with open(os.path.join(os.path.dirname(__file__), "cats.jpg"), "rb") as f:
        return base64.b64encode(f.read())


@pytest.fixture
def image_url() -> str:
    return "https://images.unsplash.com/photo-1518791841217-8f162f1e1131?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=800&q=60"


@pytest.fixture
def dog_image_url() -> str:
    return "https://live.staticflickr.com/7396/8728178651_912c2fa554_b.jpg"


@pytest.fixture
def dog_image_id(client: TestClient, dog_image_url: str):
    response = client.post(
        "/images",
        json={
            "label": "test",
            "analyze_image": True,
            "image_url": dog_image_url,
        },
    )
    resp_body = response.json()
    return resp_body["id"]


@pytest.fixture
def analyzed_image_id(client: TestClient, encoded_image_string) -> int:
    response = client.post(
        "/images",
        json={
            "label": "test",
            "analyze_image": True,
            "image_data": encoded_image_string.decode("utf-8"),
        },
    )
    return response.json()["id"]


def test_can_upload_and_analyze_image_from_url(client: TestClient, image_url: str):
    response = client.post(
        "/images",
        json={
            "label": "test",
            "analyze_image": True,
            "image_url": image_url,
        },
    )
    assert response.status_code == 200
    resp_body = response.json()
    assert resp_body["label"] == "test"
    assert resp_body["objects"] is not None
    assert "cat" in resp_body["objects"]


def test_can_upload_and_analyze_image_from_base64(
    client: TestClient, encoded_image_string
):
    response = client.post(
        "/images",
        json={
            "label": "test",
            "analyze_image": True,
            "image_data": encoded_image_string.decode("utf-8"),
        },
    )
    assert response.status_code == 200
    resp_body = response.json()
    assert resp_body["label"] == "test"
    assert resp_body["objects"] is not None
    assert "cat" in resp_body["objects"]


def test_cannot_use_both_url_and_base64_string(
    client: TestClient, encoded_image_string, image_url
):
    response = client.post(
        "/images",
        json={
            "label": "test",
            "image_data": encoded_image_string.decode("utf-8"),
            "image_url": image_url,
        },
    )
    assert response.status_code == 400
    resp_body = response.json()
    assert resp_body["detail"] == "Cannot provide both image_url and image_data"


def test_must_include_one_of_url_or_base64_string(client: TestClient):
    response = client.post(
        "/images",
        json={
            "label": "test",
            "analyze_image": True,
        },
    )
    assert response.status_code == 400
    resp_body = response.json()
    assert resp_body["detail"] == "Must provide one of image_url or image_data"


def test_must_provide_valid_url(client: TestClient):
    not_a_url = "not a url"
    response = client.post(
        "/images",
        json={
            "label": "test",
            "analyze_image": True,
            "image_url": not_a_url,
        },
    )
    assert response.status_code == 400
    resp_body = response.json()
    assert resp_body["detail"] == f"{not_a_url} is an invalid URL"


def test_valid_url_that_does_not_exist_should_fail(client: TestClient):
    not_there_url = "https://not-a-url.com"
    response = client.post(
        "/images",
        json={
            "label": "test",
            "analyze_image": True,
            "image_url": not_there_url,
        },
    )
    assert response.status_code == 400
    resp_body = response.json()
    assert (
        resp_body["detail"]
        == f"An error occured accessing the image at {not_there_url}"
    )


def test_get_image_by_id(client: TestClient, analyzed_image_id: int):
    response = client.get(f"/images/{analyzed_image_id}")
    assert response.status_code == 200

    resp_body = response.json()
    assert resp_body["id"] == analyzed_image_id
    assert resp_body["label"] == "test"
    assert resp_body["objects"] is not None
    assert "cat" in resp_body["objects"]


def test_get_image_by_id_that_does_not_exist_should_fail(client: TestClient):
    response = client.get("/images/9999")
    assert response.status_code == 404
    resp_body = response.json()
    assert resp_body["detail"] == "Image not found"


def test_get_all_images(client: TestClient, analyzed_image_id: int):
    response = client.get("/images")
    assert response.status_code == 200
    resp_body = response.json()
    assert any(image["id"] == analyzed_image_id for image in resp_body)


def test_get_all_images_with_object_filter(client: TestClient, analyzed_image_id: int):
    response = client.get("/images?object=cat")
    assert response.status_code == 200
    resp_body = response.json()
    assert any(image["id"] == analyzed_image_id for image in resp_body)


def test_get_images_with_nonexisiting_object_filter(client: TestClient):
    response = client.get("/images?objects=not-a-cat")
    assert response.status_code == 200
    resp_body = response.json()
    assert len(resp_body) == 0


def test_filter_images_should_not_include_unspecified_objects(
    client: TestClient, analyzed_image_id: int, dog_image_id: int
):
    response = client.get("/images?objects=cat")
    assert response.status_code == 200
    resp_body = response.json()
    assert not any(image["id"] == dog_image_id for image in resp_body)


def test_image_should_not_be_analyzed_if_not_requested(
    client: TestClient, image_url: str
):
    response = client.post(
        "/images",
        json={
            "label": "test",
            "analyze_image": False,
            "image_url": image_url,
        },
    )
    resp_body = response.json()
    assert len(resp_body["objects"]) == 0


def test_label_should_be_generated_if_not_provided(client: TestClient, image_url: str):
    response = client.post(
        "/images",
        json={
            "analyze_image": False,
            "image_url": image_url,
        },
    )
    resp_body = response.json()
    assert resp_body["label"] and resp_body["label"] != ""
