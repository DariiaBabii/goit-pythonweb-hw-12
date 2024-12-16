from sqlalchemy.orm import Session
from contacts_api.models import Contact, User
from datetime import date, timedelta

def get_contacts(db: Session, user_id: int):
    """
    Retrieves all contacts for a specific user.

    Args:
        db (Session): The database session object.
        user_id (int): The ID of the user whose contacts are to be retrieved.

    Returns:
        list: A list of Contact objects associated with the given user_id.
    """
    return db.query(Contact).filter(Contact.user_id == user_id).all()

def get_contact_by_id(db: Session, user_id: int, contact_id: int):
    """
    Retrieves a specific contact by its ID for a given user.

    Args:
        db (Session): The database session object.
        user_id (int): The ID of the user associated with the contact.
        contact_id (int): The ID of the contact to retrieve.

    Returns:
        Contact or None: The Contact object if found, otherwise None.
    """
    return db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == user_id).first()

def create_contact(db: Session, user_id: int, contact_data: dict):
    """
    Creates a new contact and saves it to the database.

    Args:
        db (Session): The database session object.
        user_id (int): The ID of the user to associate with the new contact.
        contact_data (dict): A dictionary containing the contact's information.

    Returns:
        Contact: The created Contact object.
    """
    contact = Contact(**contact_data, user_id=user_id)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact

def update_contact(db: Session, user_id: int, contact_id: int, update_data: dict):
    """
    Updates an existing contact with new data.

    Args:
        db (Session): The database session object.
        user_id (int): The ID of the user associated with the contact.
        contact_id (int): The ID of the contact to update.
        update_data (dict): A dictionary containing the updated contact data.

    Returns:
        Contact or None: The updated Contact object if found, otherwise None.
    """
    contact = get_contact_by_id(db, user_id, contact_id)
    if contact is None:
        return None
    for key, value in update_data.items():
        setattr(contact, key, value)
    db.commit()
    return contact

def delete_contact(db: Session, user_id: int, contact_id: int):
    """
    Deletes a specific contact from the database.

    Args:
        db (Session): The database session object.
        user_id (int): The ID of the user associated with the contact.
        contact_id (int): The ID of the contact to delete.

    Returns:
        Contact or None: The deleted Contact object if it existed, otherwise None.
    """
    contact = get_contact_by_id(db, user_id, contact_id)
    if contact:
        db.delete(contact)
        db.commit()
    return contact

def search_contacts(db: Session, user_id: int, query: str):
    """
    Searches for contacts that match the query in the user's contact list.

    Args:
        db (Session): The database session object.
        user_id (int): The ID of the user whose contacts to search.
        query (str): The search query string.

    Returns:
        list: A list of Contact objects that match the search criteria.
    """
    return db.query(Contact).filter(
        Contact.user_id == user_id,
        (
            (Contact.first_name.ilike(f"%{query}%")) |
            (Contact.last_name.ilike(f"%{query}%")) |
            (Contact.email.ilike(f"%{query}%"))
        )
    ).all()

def get_upcoming_birthdays(db: Session, user_id: int):
    """
    Retrieves contacts with upcoming birthdays within the next 7 days.

    Args:
        db (Session): The database session object.
        user_id (int): The ID of the user whose contacts to check for birthdays.

    Returns:
        list: A list of Contact objects with birthdays in the upcoming week.
    """
    today = date.today()
    upcoming = today + timedelta(days=7)
    return db.query(Contact).filter(
        Contact.user_id == user_id,
        Contact.birthday.between(today, upcoming)
    ).all()
