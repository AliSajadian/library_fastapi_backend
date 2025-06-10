from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class CategoryBase(BaseModel):
    name: str
    parent_id: Optional[UUID] = None


class CategoryCreate(BaseModel):
    name: str
    parent_id: Optional[UUID] = None
    model_config = ConfigDict(
        from_attributes= True,
        json_schema_extra={
            "example":{
                "name":"sample name",
                "parent_id": "" 
            }
        }
    )


class CategoryUpdate(CategoryBase):
    pass

# class CategoryTree(CategoryBase):
#     children: List['CategoryTree'] = []
#     books: list = []


class CategoryRead(CategoryBase):
    id: UUID
    books: List[dict] = []  # Or BookBase if defined
    children: List["CategoryRead"] = []

    class Config:
        from_attributes=True

CategoryRead.model_rebuild()
