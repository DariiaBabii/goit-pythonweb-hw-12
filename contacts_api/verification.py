from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from contacts_api.database import get_db
from contacts_api.models import User
from contacts_api.dependencies import create_email_token, verify_email_token
from contacts_api.user import get_current_user, send_email_verification

router = APIRouter()

@router.post("/verify-email/")
def send_verification_email(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Sends a verification email to the user.

    Args:
        user (User): The currently authenticated user.
        db (Session): Database session.

    Raises:
        HTTPException: If the user's email is already verified.

    Returns:
        dict: A message indicating the email was sent.
    """
    if user.is_verified:
        raise HTTPException(status_code=400, detail="Email already verified.")
    token = create_email_token(user.email)
    send_email_verification(user.email, token)  
    return {"message": "Verification email sent."}

@router.get("/verify-email/{token}")
def verify_email(token: str, db: Session = Depends(get_db)):
    """Verifies a user's email using a token.

    Args:
        token (str): The email verification token.
        db (Session): Database session.

    Raises:
        HTTPException: If the user is not found.

    Returns:
        dict: A message indicating successful email verification.
    """
    email = verify_email_token(token)
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user.is_verified = True
    db.commit()
    return {"message": "Email verified successfully."}
