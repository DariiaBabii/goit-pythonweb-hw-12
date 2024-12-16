import pytest
from fastapi.testclient import TestClient
from contacts_api.main import app 
from unittest.mock import patch

@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client

@pytest.fixture
def mock_cloudinary():
    with patch("cloudinary.uploader.upload") as mock_upload:
        yield mock_upload

@pytest.fixture
def mock_send_email():
    with patch("contacts_api.user.aiosmtplib.send") as mock_send:
        yield mock_send
