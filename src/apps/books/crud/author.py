import logging
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.exc import IntegrityError

from src.apps.books.models import Author, Book
from ..exceptions import ObjectVerificationError, ObjectCreationError, ObjectNotFoundError

class AuthorCRUD:
    """ ==================== """
    """ Authors API Services """
    """ ==================== """
    async def add(self, db: AsyncSession, author: Author):
        """
        Create author object
        """
        try:
            db.add(author)
            await db.commit()
            await db.refresh(author)
            
            logging.info(f"Created new author.")
            return author
    
        except ValidationError as e:
            logging.error(f"Failed to the author data verification. Error: {str(e)}")
            await db.rollback()
            raise ObjectVerificationError("Author", str(e))
        except Exception as e:
            logging.error(f"Failed to create author. Error: {str(e)}")
            await db.rollback()
            raise ObjectCreationError(str(e))        


    async def get_all(self, db: AsyncSession):
        """
        Get all Authors objects from db
        """
        statement = select(Author).order_by(Author.id)

        result = await db.execute(statement)
        authors = result.scalars().all()
        
        logging.info(f"Retrieved {len(authors)} authors.")
        return authors


    async def get_by_id(
        self, db: AsyncSession, author_id: int
    ):
        """
        Get author by id
        """
        try:
            statement = select(Author).filter(Author.id == author_id)
            result = await db.execute(statement)           
            author = result.scalars().one()
            logging.info(f"Retrieved author {author_id}.")
            return author
        except NoResultFound:
            logging.warning(f"Author with id {author_id} not found.")
            raise ObjectNotFoundError("Author", author_id)
            
        
    async def get_books_by_id(
        self, db: AsyncSession, author_id: int
    ):
        """
        Get author by id
        """
        # First check if the author exists
        author_stmt = select(Author).filter(Author.id == author_id)
        author_result = await db.execute(author_stmt)
        author = author_result.scalar_one_or_none()

        if not author:
            logging.warning(f"Author with id {author_id} not found.")
            raise ObjectNotFoundError("Author", author_id)
        
        # Author exists, now get books
        books_stmt = select(Book).filter(Book.author_id == author_id).order_by(Book.id)
        books_result = await db.execute(books_stmt)
        books = books_result.scalars().all()
        
        logging.info(f"Retrieved {len(books)} books of author {author_id}.")
        return books
            

    async def update(
        self, db: AsyncSession, author_id, data
    ):
        """
        Update Author by id
        """
        statement = select(Author).filter(Author.id == author_id)

        result = await db.execute(statement)
        author = result.scalars().scalar_one_or_none()

        if not author:
            logging.warning(f"Author {author_id} not found.")
            raise ObjectNotFoundError("Author", author_id)
        
        author.name = data["name"]

        await db.commit()
        await db.refresh(author)

        logging.info(f"Successfully updated author {author_id}.")
        return author


    async def delete(self, db: AsyncSession, author: Author):
        """delete author by id
        """
        await db.delete(author)
        await db.commit()
        await db.refresh(author)

        logging.info(f"Successfully deleted author {author.id}.")
        return {}
       