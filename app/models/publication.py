from typing import Optional

from sqlmodel import Field, SQLModel


class Publication(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    year: int = Field(index=True)
    venue: str = ""


class PublicationAuthor(SQLModel, table=True):
    """Many-to-many: publication ↔ author (coauthor)."""

    publication_id: int = Field(foreign_key="publication.id", primary_key=True)
    author_id: int = Field(foreign_key="author.id", primary_key=True)
