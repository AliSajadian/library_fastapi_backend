from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class PublisherBase(BaseModel):
    id: UUID
    name: str = Field(min_length=3, max_length=100)


class PublisherCreate(BaseModel):
    name: str
    
    model_config = ConfigDict(
        from_attributes= True,
        json_schema_extra={
            "example":{
                "name":"sample name",
            }
        }
    )

class PublisherRead(BaseModel):
    id: UUID
    name : str

    class Config:
        orm_mode = True
