import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship 

from src.core.database import Base
from src.apps.books.models import Book


class BookCategory(Base):
    __tablename__ = 'book_categories'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey('book_categories.id'), nullable=True)

    parent = relationship("BookCategory", remote_side=[id], back_populates="children")
    children = relationship("BookCategory", back_populates="parent", cascade="all, delete")

    books = relationship("Book", back_populates="category")
