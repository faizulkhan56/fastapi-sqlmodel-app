from typing import List, Optional

from sqlmodel import Session, select

from .models import Book
from .schemas import BookCreate, BookUpdate


def create_book(session: Session, book: BookCreate) -> Book:
    """Create a new Book in the database."""
    db_book = Book.from_orm(book)
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return db_book


def get_book(session: Session, book_id: int) -> Optional[Book]:
    """Return a single Book by primary key, or None if not found."""
    return session.get(Book, book_id)


def get_books(session: Session, offset: int = 0, limit: int = 10) -> List[Book]:
    """Return a page of books."""
    statement = select(Book).offset(offset).limit(limit)
    return session.exec(statement).all()


def update_book(session: Session, book_id: int, book_data: BookUpdate) -> Optional[Book]:
    """Apply partial update to a Book and return it, or None if not found."""
    db_book = session.get(Book, book_id)
    if not db_book:
        return None

    for key, value in book_data.dict(exclude_unset=True).items():
        setattr(db_book, key, value)

    db_book.update_timestamp()
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return db_book


def delete_book(session: Session, book_id: int) -> bool:
    """Delete a Book. Returns True on success, False if not found."""
    db_book = session.get(Book, book_id)
    if not db_book:
        return False

    session.delete(db_book)
    session.commit()
    return True
