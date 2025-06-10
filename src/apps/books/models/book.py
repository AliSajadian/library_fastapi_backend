import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Date, String, Integer, ForeignKey
from sqlalchemy.orm import relationship 

from src.core.database import Base
from src.apps.books.models import Author
    
class Book(Base):
    __tablename__: str = 'books'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False, unique=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey('book_categories.id'), nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey('book_authors.id'), nullable=False)
    publisher_id = Column(UUID(as_uuid=True), ForeignKey('book_publishers.id'), nullable=False)
    published_at = Column(Date, nullable=True)
    description = Column(String)
    rating = Column(Integer, nullable=False)
    
    category = relationship("BookCategory", back_populates="books")
    publisher = relationship("BookPublisher", back_populates="books")
    author = relationship("Author", back_populates="books")
    
    def __repr__(self, title=None, author=None):
        self.title = f"{title if title is not None else ''}, {author if author is not None else ''}"
         
        
