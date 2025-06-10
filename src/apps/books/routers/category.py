from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException, Path
from typing import List
from uuid import UUID

from src.api.dependencies.database import AsyncDbSession
from src.apps.books.models.category import BookCategory
from src.apps.books.schemas.category import CategoryRead, CategoryCreate, CategoryUpdate
from src.apps.books.crud import CategoryCRUD

routers = APIRouter()
services = CategoryCRUD()


""" ========================= """
""" Category router endpoints """
""" ========================= """
@routers.post("/", status_code=HTTPStatus.CREATED, response_model=None)
async def create(data: CategoryCreate, db: AsyncDbSession):
    """API endpoint for creating a category resource

    Args:
        category_data (AuthorCreateModel): data for creating a category using the category schema

    Returns:
        dict: category that has been created
    """
    new_category = BookCategory(
        name=data.name, 
        parent_id=data.parent_id if data.parent_id else None
    )
    return await services.add(db, new_category)


@routers.get("/tree", response_model=List[CategoryRead])
async def get_category_tree(db: AsyncDbSession):
    """API endpoint for listing all category hierarchy
    """
    categories = await services.get_all_tree(db)
    return [CategoryRead.model_validate(cat) for cat in categories]


@routers.get("/{category_id}", response_model=CategoryRead)
async def get_category_by_id(category_id: UUID, db: AsyncDbSession):
    """API endpoint for retrieving a category by its ID

    Args:
        category_id (int): the ID of the category to retrieve

    Returns:
        dict: The retrieved category
    """
    category = await services.get_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return CategoryRead.from_orm(category)


@routers.get("/{category_id}/books")
async def get_books_by_id(db: AsyncDbSession, 
    category_id: int = Path(..., description="The category id, you want to find: ", gt=0),
    # query_param: str = Query(None, max_length=5)
):
    """API endpoint for retrieving a category by its ID

    Args:
        category_id (int): the ID of the category to retrieve

    Returns:
        dict: The retrieved roles
    """
    roles = await services.get_books_by_id(db, category_id)
    return roles


@routers.put("/{category_id}", response_model=CategoryRead)
async def update(category_id: UUID, data: CategoryUpdate, db: AsyncDbSession):
    """Update by ID

    Args:
        category_id (int): ID of category to update
        data (AuthorCreateModel): data to update category

    Returns:
        dict: the updated category
    """
    updated = await services.update(db, category_id, data)
    return updated


@routers.delete("/{category_id}", response_model=CategoryRead)
async def delete(category_id: UUID, db: AsyncDbSession):
    """Delete category by id

    Args:
        category_id (str): ID of category to delete
    """
    deleted = await services.delete(db, category_id)
    return deleted
