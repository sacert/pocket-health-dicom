import os
import pytest
from app import app, DICOM_FOLDER
from io import BytesIO
from unittest.mock import patch
from pydicom.errors import InvalidDicomError
import numpy as np


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown():
    os.makedirs(DICOM_FOLDER, exist_ok=True)
    yield
    for file in os.listdir(DICOM_FOLDER):
        os.remove(os.path.join(DICOM_FOLDER, file))


def test_upload_valid_dicom(client):
    with patch("pydicom.dcmread") as mock_dcmread:
        mock_dcmread.return_value = True
        data = {"file": (BytesIO(b"Test DICOM content"), "test.dcm")}
        response = client.post("/upload", data=data, content_type="multipart/form-data")
        assert response.status_code == 200
        assert response.json["message"] == "Sucessfully uploaded"


def test_upload_missing_file(client):
    response = client.post("/upload")
    assert response.status_code == 400
    assert response.json["error"] == "Missing file"


def test_upload_invalid_dicom(client):
    with patch("pydicom.dcmread", side_effect=InvalidDicomError):
        data = {"file": (BytesIO(b"Invalid content"), "test.dcm")}
        response = client.post("/upload", data=data, content_type="multipart/form-data")
        assert response.status_code == 400
        assert "Error processing DICOM file" in response.json["error"]


def test_get_dicom_header_attribute_valid(client):
    filename = "test.dcm"
    file_path = os.path.join(DICOM_FOLDER, filename)
    with open(file_path, "wb") as f:
        f.write(b"Test DICOM content")

    with patch("pydicom.dcmread") as mock_dcmread:
        mock_dcmread.return_value = {(int("0010", 16), int("0010", 16)): "Test Patient"}
        response = client.get(
            "/dicom-header-attribute",
            query_string={"filename": filename, "tag": "0010,0010"},
        )
        assert response.status_code == 200
        assert response.json["attribute"] == "Test Patient"


def test_get_dicom_header_attribute_missing_tag(client):
    response = client.get(
        "/dicom-header-attribute", query_string={"filename": "test.dcm"}
    )
    assert response.status_code == 400
    assert response.json["error"] == "Please specify tag"


def test_get_dicom_header_attribute_invalid_tag(client):
    filename = "test.dcm"
    file_path = os.path.join(DICOM_FOLDER, filename)
    with open(file_path, "wb") as f:
        f.write(b"Test DICOM content")

    with patch("pydicom.dcmread") as mock_dcmread:
        mock_dcmread.return_value = {(int("0010", 16), int("0010", 16)): "Test Patient"}
        response = client.get(
            "/dicom-header-attribute",
            query_string={"filename": "test.dcm", "tag": "invalid_tag"},
        )
        assert response.status_code == 400
        assert "Invalid structure for tag" in response.json["error"]


def test_convert_to_png_valid(client):
    filename = "test.dcm"
    file_path = os.path.join(DICOM_FOLDER, filename)
    with open(file_path, "wb") as f:
        f.write(b"Test DICOM content")

    with patch("pydicom.dcmread") as mock_dcmread:
        mock_dcmread.return_value.pixel_array = np.array([[0, 1], [1, 0]])

        response = client.get("/convert-to-png", query_string={"filename": filename})
        assert response.status_code == 200
        assert response.content_type == "image/png"


def test_convert_to_png_missing_file(client):
    response = client.get(
        "/convert-to-png", query_string={"filename": "non_existent.dcm"}
    )
    assert response.status_code == 404
    assert response.json["error"] == "File not found"


def test_convert_to_png_invalid_dicom(client):
    filename = "invalid.dcm"
    file_path = os.path.join(DICOM_FOLDER, filename)
    with open(file_path, "wb") as f:
        f.write(b"Invalid DICOM content")

    with patch("pydicom.dcmread", side_effect=InvalidDicomError):
        response = client.get("/convert-to-png", query_string={"filename": filename})
        print(response)
        assert response.status_code == 400
        assert (
            "Error processing DICOM file; The specified file is not a valid DICOM file."
            in response.json["error"]
        )
