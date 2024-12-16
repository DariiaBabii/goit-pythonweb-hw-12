from contacts_api.repositories import UserRepository
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from contacts_api.models import User

def test_update_avatar(mock_cloudinary):
    db = MagicMock(Session)
    
    user = User(id=1, email="user@example.com", avatar_url=None)
    
    mock_cloudinary.return_value = {"secure_url": "http://mock-url.com/avatar.jpg"}
    
    repo = UserRepository(db)
    
    result = repo.update_avatar(user, "mock_file")
    
    assert result["avatar_url"] == "http://mock-url.com/avatar.jpg"
