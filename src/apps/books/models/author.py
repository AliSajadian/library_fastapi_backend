import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship 

from src.core.database import Base

class Author(Base):
    __tablename__: str = 'book_authors'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)

    books = relationship("Book", back_populates="author", uselist=True)
    
    def __repr__(self):
        return f"<Author(name='{self.name}', email='{self.email}')>"
    