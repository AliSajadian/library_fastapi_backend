from fastapi import APIRouter, Path
from http import HTTPStatus
from typing import List

from src.api.dependencies.auth import CurrentUser
from src.api.dependencies.database import AsyncDbSession
from ...apps.books.models import Author, Book
from ...apps.books.crud import AuthorServices, BookServices
from ...apps.books.schemas import AuthorModel, AuthorCreateModel, BookModel, BookCreateModel
 

""" ======================= """
""" Author router endpoints """
""" ======================= """
author_router_ = APIRouter()
services = AuthorServices()

@author_router_.post("", status_code=HTTPStatus.CREATED)
async def create_author(db: AsyncDbSession, current_user: CurrentUser, author_data: AuthorCreateModel):
    """API endpoint for creating a author resource

    Args:
        author_data (AuthorCreateModel): data for creating a author using the author schema

    Returns:
        dict: author that has been created
    """
    new_author = Author(
        name=author_data.name, 
    )
    author = await services.add(db, new_author)
    return author


@author_router_.get("", response_model=List[AuthorModel])
async def get_all_authors(db: AsyncDbSession):
    """API endpoint for listing all author resources
    """
    authors = await services.get_all(db)
    return authors


@author_router_.get("/{author_id}")
async def get_author_by_id(db: AsyncDbSession, 
    author_id: int = Path(..., description="The author id, you want to find: ", gt=1)
):
    """API endpoint for retrieving a author by its ID

    Args:
        author_id (int): the ID of the author to retrieve

    Returns:
        dict: The retrieved author
    """
    author = await services.get_by_id(db, author_id)
    return author


@author_router_.get("/{author_id}/books")
async def get_books_by_author_id(db: AsyncDbSession, 
    author_id: int = Path(..., description="The author's books, you want to find: ")
):
    """API endpoint for retrieving a author by its ID

    Args:
        author_id (int): the ID of the author to retrieve

    Returns:
        dict: The retrieved author
    """
    books = await services.get_books_by_id(db, author_id)
    return books


@author_router_.patch("/{author_id}")
async def update_author(db: AsyncDbSession, data: AuthorCreateModel, author_id: int = Path(..., description="The author's books, you want to find: ")):
    """Update by ID

    Args:
        author_id (int): ID of author to update
        data (AuthorCreateModel): data to update author

    Returns:
        dict: the updated author
    """
    author = await services.update(
        db, 
        author_id, 
        data={
            "name": data.name
        }
    )

    return author


@author_router_.delete("/{author_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_author(db: AsyncDbSession, author_id: int = Path(..., description="The author id, you want to delete: ")) -> None:
    """Delete author by id

    Args:
        author_id (str): ID of author to delete

    """
    author = await services.get_by_id(db, author_id)
    await services.delete(db, author)
    return 


""" ===================== """
""" Book router endpoints """
""" ===================== """
book_router = APIRouter(
    # prefix="/",
    # tags=["books"],
    # dependencies=[Depends(get_db)],
    # responses={404: {"description": "Not found"}},
)
services = BookServices()

@book_router.post("", status_code=HTTPStatus.CREATED)
async def create_book(db: AsyncDbSession, book_data: BookCreateModel):
    """API endpoint for creating a book resource

    Args:
        book_data (BookCreateModel): data for creating a book using the book schema

    Returns:
        dict: book that has been created
    """
    new_book = Book(
        title=book_data.title, 
        author_id=book_data.author_id, 
        description=book_data.description, 
        rating=book_data.rating
    )
    book = await services.add(db, new_book)
    return book


@book_router.get("", response_model=List[BookModel])
async def get_all_books(db: AsyncDbSession):
    """API endpoint for listing all book resources
    """
    books = await services.get_all(db)
    return books


@book_router.get("/{book_id}")
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
    book = await services.get_by_id(db, book_id)
    return book


@book_router.patch("/{book_id}")
async def update_book(db: AsyncDbSession, data: BookCreateModel, 
                      book_id: int = Path(..., description="The book id, you want to update: ")):
    """Update by ID

    Args:
        book_id (int): ID of book to update
        data (BookCreateModel): data to update book

    Returns:
        dict: the updated book
    """
    book = await services.update(
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


@book_router.delete("/{book_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_book(db: AsyncDbSession, book_id: int = Path(..., description="The book id, you want to delete: ")) -> None:
    """Delete book by id

    Args:
        book_id (str): ID of book to delete
    """
    book = await services.get_by_id(db, book_id)
    result = await services.delete(db, book)
    return result