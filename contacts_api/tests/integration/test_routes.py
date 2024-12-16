import pytest
from fastapi.testclient import TestClient
from contacts_api.main import app
from unittest.mock import patch

@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client

def test_update_avatar(client, mock_cloudinary):
    mock_cloudinary.return_value = {"secure_url": "http://mock-url.com/avatar.jpg"}
    
    headers = {"Authorization": "Bearer mock_token"}
    
    with open("test_avatar.jpg", "rb") as f:
        response = client.put(
            "/me/avatar/",
            files={"file": ("test_avatar.jpg", f, "image/jpeg")},
            headers=headers
        )
    
    assert response.status_code == 200
    assert response.json() == {"message": "Avatar updated successfully.", "avatar_url": "http://mock-url.com/avatar.jpg"}
