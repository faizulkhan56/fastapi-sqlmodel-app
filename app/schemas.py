from typing import Optional, List
from datetime import datetime

from sqlmodel import SQLModel


class BookCreate(SQLModel):
    """Payload for creating a new book."""

    title: str
    author: str
    year: int
    price: float
    in_stock: bool = True
    description: Optional[str] = None


class BookRead(SQLModel):
    """Response model for reading a book from the API."""

    id: int
    title: str
    author: str
    year: int
    price: float
    in_stock: bool
    description: Optional[str]
    created_at: datetime
    updated_at: datetime


class BookUpdate(SQLModel):
    """Payload for partially updating an existing book."""

    title: Optional[str] = None
    author: Optional[str] = None
    year: Optional[int] = None
    price: Optional[float] = None
    in_stock: Optional[bool] = None
    description: Optional[str] = None


class BookSearchResults(SQLModel):
    """Wrapper for paginated search results (not wired in router yet)."""

    results: List[BookRead]
    total: int
    page: int
    size: int
