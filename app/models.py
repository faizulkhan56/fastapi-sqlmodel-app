from typing import Optional
from datetime import datetime

from sqlmodel import SQLModel, Field


class BookBase(SQLModel):
    """Fields shared by all representations of a Book."""

    title: str = Field(index=True)
    author: str = Field(index=True)
    year: int
    price: float
    in_stock: bool = True
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class Book(BookBase, table=True):
    """Database table representation of a Book."""

    id: Optional[int] = Field(default=None, primary_key=True)

    def update_timestamp(self) -> None:
        self.updated_at = datetime.utcnow()
