from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from .crud import create_book, get_books, get_book, update_book, delete_book
from .schemas import BookCreate, BookRead, BookUpdate
from .database import get_session

router = APIRouter()


@router.post("/books/", response_model=BookRead)
def create(book: BookCreate, session: Session = Depends(get_session)):
    """Create a new book."""
    return create_book(session, book)


@router.get("/books/", response_model=List[BookRead])
def read_all(
    offset: int = 0,
    limit: int = Query(default=10, le=100),
    session: Session = Depends(get_session),
):
    """Return a paginated list of books."""
    return get_books(session, offset, limit)


@router.get("/books/{book_id}", response_model=BookRead)
def read(book_id: int, session: Session = Depends(get_session)):
    """Return a single book by ID."""
    book = get_book(session, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.put("/books/{book_id}", response_model=BookRead)
def update(book_id: int, book_data: BookUpdate, session: Session = Depends(get_session)):
    """Update an existing book."""
    book = update_book(session, book_id, book_data)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.delete("/books/{book_id}")
def delete(book_id: int, session: Session = Depends(get_session)):
    """Delete a book by ID."""
    if not delete_book(session, book_id):
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book deleted successfully"}
