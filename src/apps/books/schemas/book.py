from datetime import date
from pydantic import BaseModel, Field, ConfigDict


from typing import List
from uuid import UUID
from pydantic import BaseModel


class BookBase(BaseModel):
    title: str

    class Config:
        from_attributes= True


class CategoryRead(BaseModel):
    id: UUID
    name: str
    books: List[BookBase] = []
    children: List["CategoryRead"] = []

    class Config:
        from_attributes= True

CategoryRead.model_rebuild()


class BookModel(BaseModel):
    id: UUID
    title: str = Field(min_length=0, max_length=100)
    author_id: UUID
    publisher_id: UUID
    published_at: date
    description: str = Field(min_length=0, max_length=100)
    rating: int = Field(gt=-1, lt=101)

    model_config = ConfigDict(
        from_attributes= True
    )

#schema for creating a note
class BookCreateModel(BaseModel):
    title : str
    category_id: UUID
    author_id: UUID
    publisher_id: UUID
    published_at: date
    description: str
    rating: int
    
    model_config = ConfigDict(
        from_attributes= True,
        json_schema_extra={
            "example":{
                "title":"Sample title",
                "category_id": "",
                "author_id": "",
                "publisher_id": "",
                "published_at": "2023-10-01",
                "description": "Sample description", 
                "rating": "100"               
            }
        }
    )