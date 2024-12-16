import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException
from contacts_api.config import settings

# Secret key and encryption algorithm
SECRET_KEY = settings.JWT_SECRET_KEY 
ALGORITHM = "HS256"

TOKEN_EXPIRE_HOURS = 24  
RESET_TOKEN_EXPIRE_HOURS = 1  

def create_token(payload: dict, expiration_hours: int) -> str:
    """
    Generates a JWT token based on the provided payload and expiration time.

    Args:
        payload (dict): The payload to be included in the token.
        expiration_hours (int): The number of hours until the token expires.

    Returns:
        str: The generated JWT token.
    """
    payload["exp"] = datetime.utcnow() + timedelta(hours=expiration_hours)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> dict:
    """
    Verifies a JWT token and decodes the payload.

    Args:
        token (str): The JWT token to be verified and decoded.

    Returns:
        dict: The decoded payload from the token.

    Raises:
        HTTPException: If the token is expired or invalid, raises a 400 HTTP error 
        with an appropriate message.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=400, detail="Invalid token")

def create_email_token(email: str) -> str:
    """
    Generates a JWT token for email verification.

    Args:
        email (str): The email address for which the token is generated.

    Returns:
        str: The generated JWT token that can be used for email verification.
    """
    payload = {"sub": email}
    return create_token(payload, TOKEN_EXPIRE_HOURS)

def verify_email_token(token: str) -> str:
    """
    Verifies an email verification token and returns the email address.

    Args:
        token (str): The JWT token to be verified and decoded.

    Returns:
        str: The email address embedded in the token payload.
    """
    payload = verify_token(token)
    return payload.get("sub")

def generate_reset_token(user_email: str) -> str:
    """Generates a password reset token."""
    payload = {"email": user_email}
    return create_token(payload, RESET_TOKEN_EXPIRE_HOURS)

def verify_reset_token(token: str) -> str:
    """Verifies the reset token and returns the email if valid."""
    payload = verify_token(token)
    return payload["email"]
