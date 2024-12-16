from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from auth import get_current_user
from crud import get_contacts, create_contact, update_contact, delete_contact
from database import get_db

router = APIRouter()

@router.get("/contacts")
def read_contacts(db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    return get_contacts(db, user_id=user)

@router.post("/contacts")
def create_new_contact(contact_data: dict, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    return create_contact(db, user_id=user, contact_data=contact_data)

@router.put("/contacts/{contact_id}")
def update_existing_contact(contact_id: int, update_data: dict, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    contact = update_contact(db, user_id=user, contact_id=contact_id, update_data=update_data)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found or access denied")
    return contact

@router.delete("/contacts/{contact_id}")
def delete_existing_contact(contact_id: int, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    contact = delete_contact(db, user_id=user, contact_id=contact_id)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found or access denied")
    return {"detail": "Contact deleted"}