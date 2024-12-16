import os
from fastapi import APIRouter, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
from contacts_api.database import get_db
from contacts_api.models import User
from contacts_api.dependencies import get_current_user

router = APIRouter()

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)

MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/jpg"}

@router.put("/me/avatar/")
def update_avatar(
    file: UploadFile, 
    user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Updates the avatar of the authenticated user.

    Args:
        file (UploadFile): The uploaded avatar file.
        user (User): The currently authenticated user.
        db (Session): Database session.

    Raises:
        HTTPException: If the file size exceeds 2MB.
        HTTPException: If the file type is unsupported.
        HTTPException: If there's an error uploading the file.

    Returns:
        dict: Success message and the URL of the uploaded avatar.
    """

    file_size = file.file.seek(0, 2)  
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Max size is 2MB.")
    file.file.seek(0)  
    
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=415, detail="Invalid file type. Only JPEG and PNG allowed.")

    try:
        result = cloudinary.uploader.upload(file.file, folder="avatars/")
        user.avatar_url = result["secure_url"]
        db.commit()
        return {"message": "Avatar updated successfully.", "avatar_url": user.avatar_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")
