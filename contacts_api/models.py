from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    """Represents a user in the system.

    Attributes:
        id (int): Unique identifier for the user.
        username (str): Unique username of the user.
        email (str): Unique email address of the user.
        hashed_password (str): Hashed password for authentication.
        is_verified (bool): Indicates if the user's email is verified.
        avatar_url (str, optional): URL to the user's avatar image.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_verified = Column(Boolean, default=False)  
    avatar_url = Column(String, nullable=True)

class Contact(Base):
    """Represents a contact in the system.

    Attributes:
        id (int): Unique identifier for the contact.
        first_name (str): First name of the contact.
        last_name (str): Last name of the contact.
        phone_number (str): Contact's phone number.
        birthday (date): Contact's date of birth.
        extra_data (str, optional): Additional data about the contact.
        user_id (int): ID of the user who owns this contact.
        owner (User): The user that owns the contact (SQLAlchemy relationship).
    """
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    phone_number = Column(String)
    birthday = Column(Date)
    extra_data = Column(String, nullable=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="contacts")
