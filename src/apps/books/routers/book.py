from http import HTTPStatus
from typing import List
from fastapi import APIRouter, Path

from src.apps.books.crud import BookCRUD
from src.apps.books.models import Book
from src.apps.books.schemas import BookCreateModel, BookModel
from src.api.dependencies.database import AsyncDbSession


""" ===================== """
""" Book router endpoints """
""" ===================== """
routers = APIRouter()
book_services = BookCRUD()

@routers.post("", response_model=BookModel, status_code=HTTPStatus.CREATED)
async def create_book(db: AsyncDbSession, book_data: BookCreateModel):
    """API endpoint for creating a book resource

    Args:
        book_data (BookCreateModel): data for creating a book using the book schema

    Returns:
        dict: book that has been created
    """
    new_book = Book(
        title=book_data.title, 
        category_id=book_data.category_id,
        author_id=book_data.author_id, 
        publisher_id=book_data.publisher_id, 
        published_at=book_data.published_at,
        description=book_data.description,
        rating=book_data.rating
    )
    book = await book_services.add(db, new_book)
    return BookModel.model_validate(book)


@routers.get("", response_model=List[BookModel])
async def get_all_books(db: AsyncDbSession):
    """API endpoint for listing all book resources
    """
    books = await book_services.get_all(db)
    return [BookModel.model_validate(b) for b in books]


@routers.get("/{book_id}")
async def get_book_by_id(db: AsyncDbSession, 
    book_id: int = Path(..., description="The book id, you want to find: ", gt=0),
    # query_param: str = Query(None, max_length=5)
):
    """API endpoint for retrieving a book by its ID

    Args:
        book_id (int): the ID of the book to retrieve

    Returns:
        dict: The retrieved book
    """
    book = await book_services.get_by_id(db, book_id)
    return book


@routers.patch("/{book_id}")
async def update_book(db: AsyncDbSession, data: BookCreateModel, 
                      book_id: int = Path(..., description="The book id, you want to update: ")):
    """Update by ID

    Args:
        book_id (int): ID of book to update
        data (BookCreateModel): data to update book

    Returns:
        dict: the updated book
    """
    book = await book_services.update(
        db, 
        book_id, 
        data={
            "title": data.title, 
            "author_id": data.author_id, 
            "description": data.description, 
            "rating": data.rating
        }
    )
    return book

@routers.delete("/{book_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_book(db: AsyncDbSession, book_id: int = Path(..., description="The book id, you want to delete: ")) -> None:
    """Delete book by id

    Args:
        book_id (str): ID of book to delete
    """
    book = await book_services.get_by_id(db, book_id)
    result = await book_services.delete(db, book)
    return result

