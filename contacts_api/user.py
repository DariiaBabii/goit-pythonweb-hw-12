from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from contacts_api.database import get_db
from contacts_api.models import User
from contacts_api.dependencies import verify_email_token
import smtplib
from email.mime.text import MIMEText
from contacts_api.config import settings
import aiosmtplib
import json
import redis

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Retrieves the current authenticated user with Redis caching.

    Args:
        token (str): OAuth2 access token.
        db (Session): Database session.

    Raises:
        HTTPException: If the token is invalid or the user does not exist.

    Returns:
        User: The authenticated user object.
    """
    email = verify_email_token(token)

    cached_user = redis_client.get(f"user:{email}")

    if cached_user:
        return json.loads(cached_user)
    
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    redis_client.setex(f"user:{email}", 3600, json.dumps(user.dict()))  

    return user

async def send_email_verification(email: str, token: str):
    """Sends an email verification link to the user.

    Args:
        email (str): Recipient's email address.
        token (str): Verification token.

    Raises:
        HTTPException: If there's an error sending the email.
    """
    subject = "Verify your email"
    link = f"{settings.FRONTEND_URL}/verify-email/{token}"
    body = f"Click the following link to verify your email: {link}"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_USERNAME
    msg["To"] = email

    try:
        await aiosmtplib.send(
            message=msg,
            hostname=settings.SMTP_SERVER,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USERNAME,
            password=settings.SMTP_PASSWORD,
            use_tls=True,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending email: {e}")

async def send_reset_email(email: str, reset_token: str):
    """Sends a password reset email with a reset link."""
    subject = "Password Reset Request"
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
    body = f"Click the following link to reset your password: {reset_url}"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_USERNAME
    msg["To"] = email

    try:
        await aiosmtplib.send(
            message=msg,
            hostname=settings.SMTP_SERVER,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USERNAME,
            password=settings.SMTP_PASSWORD,
            use_tls=True,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending email: {e}")
