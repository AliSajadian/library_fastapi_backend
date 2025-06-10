from http import HTTPStatus
from fastapi import APIRouter
from typing import List

from src.apps.books.models import BookPublisher
from src.apps.books.schemas.publisher import PublisherRead, PublisherCreate
from src.apps.books.crud.publisher import PublisherCRUD
from src.api.dependencies.database import AsyncDbSession

routers = APIRouter()
services = PublisherCRUD()


""" ========================== """
""" Publisher router endpoints """
""" ========================== """
@routers.post("/", status_code=HTTPStatus.CREATED)
async def create(db: AsyncDbSession, data: PublisherCreate):
    """API endpoint for creating a publisher resource

    Args:
        publisher_data (PublisherCreateModel): data for creating a publisher using the publisher schema

    Returns:
        dict: publisher that has been created
    """
    new_publisher = BookPublisher(
        name=data.name, 
    )
    return await services.add(db, new_publisher)


@routers.get("/", response_model=List[PublisherRead])
async def get_all(db: AsyncDbSession):
    """API endpoint for listing all publisher resources
    """
    return await services.get_all(db)


@routers.get("/{publisher_id}", response_model=PublisherRead)
async def get_by_id(db: AsyncDbSession, publisher_id: str):
    """API endpoint for retrieving a publisher by its ID

    Args:
        publisher_id (int): the ID of the publisher to retrieve

    Returns:
        dict: The retrieved publisher
    """
    publisher = await services.get_by_id(db, publisher_id)
    return publisher


@routers.put("/{publisher_id}", response_model=PublisherRead)
async def update(db: AsyncDbSession, publisher_id: str, data: PublisherCreate):
    """Update by ID

    Args:
        author_id (int): ID of author to update
        data (AuthorCreateModel): data to update author

    Returns:
        dict: the updated author
    """
    updated = await services.update(db, data, publisher_id)
    return updated


@routers.delete("/{publisher_id}", response_model=PublisherRead)
async def delete(db: AsyncDbSession, publisher_id: str):
    """Delete author by id

    Args:
        author_id (str): ID of author to delete
    """
    deleted = await services.delete(db, publisher_id)
    return deleted
