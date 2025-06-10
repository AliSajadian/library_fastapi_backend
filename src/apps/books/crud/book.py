import logging
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.apps.books.models.book import Book
from src.apps.books.models.category import BookCategory

from ..exceptions import ObjectCreationError, ObjectNotFoundError, ObjectVerificationError


class BookCRUD:
    """ ================== """
    """ Books API Services """
    """ ================== """
    async def add(self, db: AsyncSession, book: Book):
        """
        Create book object
        """
        try:
            db.add(book)
            await db.commit()
            await db.refresh(book)
            
            logging.info(f"Created new book.")
            return book

        except Exception as e:
            logging.error(f"Failed to create book. Error: {str(e)}")
            await db.rollback()
            raise ObjectVerificationError("Book", str(e))
        except IntegrityError as e:
            logging.error(f"This publisher already exists. Error: {str(e)}")
            await db.rollback()
            raise ObjectCreationError("This publisher already exists.")
        except Exception as e:
            logging.error(f"Failed to create publisher. Error: {str(e)}")
            await db.rollback()
            raise ObjectCreationError(str(e))  
    
    async def get_all(self, db: AsyncSession):
        """
        Get all Books objects from db
        """
        statement = select(Book).order_by(Book.id)
        result = await db.execute(statement)
        books = result.scalars().all()
        
        logging.info(f"Retrieved {len(books)} books.")
        return books


    async def get_by_id(
        self, async_session: AsyncSession, book_id: int
    ):
        """
        Get book by id
        """
        async with async_session as db:
            statement = select(Book).filter(Book.id == book_id)
            
            result = await db.execute(statement)
            book = result.scalars().one_or_none()
            
            if not book:
                logging.warning(f"Book {book_id} not found.")
                raise ObjectNotFoundError("Book", book_id)
            
            logging.info(f"Retrieved book {book_id}.")
            return book


    async def get_category_tree(db: AsyncSession, parent_id=None):
        stmt = (
            select(BookCategory)
            .options(
                joinedload(BookCategory.books),
                joinedload(BookCategory.children)
            )
            .filter(BookCategory.parent_id == parent_id)
        )

        result = await db.execute(stmt)
        categories = result.scalars().all()

        # Recursively build the tree
        def build_tree(cat):
            return {
                "id": cat.id,
                "name": cat.name,
                "books": cat.books,
                "children": [build_tree(child) for child in cat.children],
            }

        return [build_tree(cat) for cat in categories]


    async def update(
        self, db: AsyncSession, book_id, data
    ):
        """
        Update Book by id
        """
        statement = select(Book).filter(Book.id == book_id)

        result = await db.execute(statement)
        book = result.scalars().one_or_none()

        if not book:
            logging.warning(f"Book {book_id} not found.")
            raise ObjectNotFoundError("Book", book_id)

        book.title = data["title"]
        book.author_id = data["author_id"]
        book.description = data["description"]
        book.rating = data["rating"]

        await db.commit()
        await db.refresh(book)

        logging.info(f"Successfully updated book {book_id}.")
        return book


    async def delete(self, db: AsyncSession, book: Book):
        """delete book by id
        """
        await db.delete(book)
        await db.commit()
        await db.refresh(book)

        logging.info(f"Successfully deleted book {book.id}.")
        return {}
    
    