"""Database table models.

Import every table model here so ``SQLModel.metadata.create_all`` sees them.
"""

from app.models.author import Author
from app.models.publication import Publication, PublicationAuthor
from app.models.user import User

__all__ = [
    "User",
    "Author",
    "Publication",
    "PublicationAuthor",
]
