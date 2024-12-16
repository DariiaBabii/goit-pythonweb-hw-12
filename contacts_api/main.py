from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from contacts_api.models import User
from contacts_api.database import engine, SessionLocal
from contacts_api import crud, models, schemas
from contacts_api.auth import decode_access_token, verify_email_token
from contacts_api.utils import hash_password  
from contacts_api.dependencies import verify_reset_token, generate_reset_token
from contacts_api.email_service import send_reset_email 
import redis
import json
from fastapi import status

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
origins = ["http://localhost:*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_db():
    """Provides a database session for dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user_from_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Retrieves the current authenticated user based on the access token."""
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = crud.get_user_by_id(db, user_id=payload["sub"])
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")
    return user

@app.get("/")
async def read_root():
    """Root endpoint providing a welcome message."""
    return {"message": "Welcome to the database"}

@app.post("/contacts/", response_model=schemas.ContactOut)
def create_contact(
    contact: schemas.ContactCreate,
    db: Session = Depends(get_db),
    user: schemas.User = Depends(get_current_user_from_token),
):
    """Creates a new contact."""
    return crud.create_contact(db, contact, user_id=user.id)

@app.get("/contacts/", response_model=list[schemas.ContactOut])
def read_contacts(
    db: Session = Depends(get_db),
    user: schemas.User = Depends(get_current_user_from_token),
):
    """Retrieves all contacts for the current user."""
    return crud.get_contacts(db, user_id=user.id)

@app.get("/contacts/{contact_id}", response_model=schemas.ContactOut)
def read_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    user: schemas.User = Depends(get_current_user_from_token),
):
    """Retrieves a specific contact by ID."""
    contact = crud.get_contact_by_id(db, contact_id)
    if not contact or contact.user_id != user.id:
        raise HTTPException(status_code=404, detail="Contact not found or access denied")
    return contact

@app.put("/contacts/{contact_id}", response_model=schemas.ContactOut)
def update_contact(
    contact_id: int,
    contact: schemas.ContactUpdate,
    db: Session = Depends(get_db),
    user: schemas.User = Depends(get_current_user_from_token),
):
    """Updates an existing contact."""
    update_contact = crud.update_contact(db, contact_id, contact, user_id=user.id)
    if not update_contact:
        raise HTTPException(status_code=404, detail="Contact not found or access denied")
    return update_contact

@app.delete("/contacts/{contact_id}", response_model=schemas.ContactOut)
def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    user: schemas.User = Depends(get_current_user_from_token),
):
    """Deletes a contact by ID."""
    delete_contact = crud.delete_contact(db, contact_id, user_id=user.id)
    if not delete_contact:
        raise HTTPException(status_code=404, detail="Contact not found or access denied")
    return delete_contact

@app.get("/contacts/search/")
def search_contacts(
    query: str,
    db: Session = Depends(get_db),
    user: schemas.User = Depends(get_current_user_from_token),
):
    """Searches for contacts based on a query string."""
    return crud.search_contacts(db, query, user_id=user.id)

@app.get("/contacts/birthdays/", response_model=list[schemas.ContactOut])
def upcoming_birthdays(
    db: Session = Depends(get_db),
    user: schemas.User = Depends(get_current_user_from_token),
):
    """Retrieves contacts with upcoming birthdays."""
    return crud.get_upcoming_birthdays(db, user_id=user.id)

@app.post("/request-password-reset")
async def request_password_reset(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    reset_token = generate_reset_token(email)
    await send_reset_email(email, reset_token)
    return {"message": "Password reset email sent"}

@app.post("/reset-password")
async def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
    email = verify_reset_token(token)
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    hashed_password = hash_password(new_password)
    user.password = hashed_password
    db.commit()

    return {"message": "Password reset successful"}

@app.get("/users/me")
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
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
