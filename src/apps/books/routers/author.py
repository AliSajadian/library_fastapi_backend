from http import HTTPStatus
from typing import List
from fastapi import APIRouter, Path

from src.apps.books.crud import AuthorCRUD
from src.apps.books.models import Author
from ..schemas.author import AuthorCreateModel, AuthorModel
from src.api.dependencies.database import AsyncDbSession


""" ======================= """
""" Author router endpoints """
""" ======================= """
routers = APIRouter()
author_services = AuthorCRUD()

@routers.post("", status_code=HTTPStatus.CREATED)
async def create_author(db: AsyncDbSession, author_data: AuthorCreateModel):
    """API endpoint for creating a author resource

    Args:
        author_data (AuthorCreateModel): data for creating a author using the author schema

    Returns:
        dict: author that has been created
    """
    new_author = Author(
        name=author_data.name, 
    )
    author = await author_services.add(db, new_author)
    return author


@routers.get("", response_model=List[AuthorModel])
async def get_all_authors(db: AsyncDbSession):
    """API endpoint for listing all author resources
    """
    authors = await author_services.get_all(db)
    return authors


@routers.get("/{author_id}")
async def get_author_by_id(db: AsyncDbSession, 
    author_id: int = Path(..., description="The author id, you want to find: ", gt=0),
    # query_param: str = Query(None, max_length=5)
):
    """API endpoint for retrieving a author by its ID

    Args:
        author_id (int): the ID of the author to retrieve

    Returns:
        dict: The retrieved author
    """
    author = await author_services.get_by_id(db, author_id)
    return author


@routers.get("/{author_id}/roles")
async def get_roles_by_author_id(db: AsyncDbSession, 
    author_id: int = Path(..., description="The author id, you want to find: ", gt=0),
    # query_param: str = Query(None, max_length=5)
):
    """API endpoint for retrieving a author by its ID

    Args:
        author_id (int): the ID of the author to retrieve

    Returns:
        dict: The retrieved roles
    """
    roles = await author_services.get_roles_by_author_id(db, author_id)
    return roles


@routers.get("/{author_id}/permissions")
async def get_permissions_by_author_id(db: AsyncDbSession, 
    author_id: int = Path(..., description="The author id, you want to find: ", gt=0),
    # query_param: str = Query(None, max_length=5)
):
    """API endpoint for retrieving permissions by author ID

    Args:
        author_id (int): the ID of the author to retrieve

    Returns:
        dict: The retrieved permissions
    """
    permissions = await author_services.get_permissions_by_author_id(db, author_id)
    return permissions


@routers.patch("/{author_id}")
async def update_author(db: AsyncDbSession, data: AuthorCreateModel, 
                      author_id: int = Path(..., description="The author id, you want to update: ")):
    """Update by ID

    Args:
        author_id (int): ID of author to update
        data (AuthorCreateModel): data to update author

    Returns:
        dict: the updated author
    """
    author = await author_services.update(
        db, 
        author_id, 
        data={
            "title": data.title, 
            "author_id": data.author_id, 
            "description": data.description, 
            "rating": data.rating
        }
    )
    return author


@routers.delete("/{author_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_author(db: AsyncDbSession, author_id: int = Path(..., description="The author id, you want to delete: ")) -> None:
    """Delete author by id

    Args:
        author_id (str): ID of author to delete
    """
    author = await author_services.get_by_id(db, author_id)
    result = await author_services.delete(db, author)
    return result
