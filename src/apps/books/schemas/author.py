from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class AuthorModel(BaseModel):
    id: UUID
    name: str = Field(min_length=3, max_length=100)
    # email : EmailStr = Field(min_length=5, max_length=100)
    # birth_date: date
    
    model_config = ConfigDict(
        from_attributes= True,
        orm_mode = True
    )


#schema for creating a note
class AuthorCreateModel(BaseModel):
    name : str
    # email : EmailStr
    # birth_date: date
    
    model_config = ConfigDict(
        from_attributes= True,
        json_schema_extra={
            "example":{
                "name":"sample name",
            }
        }
    )
    
