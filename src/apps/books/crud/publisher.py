import logging
from sqlite3 import IntegrityError
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.exc import IntegrityError

from src.apps.books.models import BookPublisher, Book
from ..exceptions import ObjectCreationError, ObjectNotFoundError, ObjectVerificationError

class PublisherCRUD:
    """ ======================= """
    """ Publishers API Services """
    """ ======================= """
    async def add(self, db: AsyncSession, publisher: BookPublisher):
        """
        Create publisher object
        """
        try:
            db.add(publisher)
            await db.commit()
            await db.refresh(publisher)
            
            logging.info(f"Created new publisher.")
            return publisher
    
        except ValidationError as e:
            logging.error(f"Failed to the publisher data verification. Error: {str(e)}")
            await db.rollback()
            raise ObjectVerificationError("Book publisher", str(e))
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
        Get all Publishers objects from db
        """
        statement = select(BookPublisher).order_by(BookPublisher.id)

        result = await db.execute(statement)
        publishers = result.scalars().all()
        
        logging.info(f"Retrieved {len(publishers)} publishers.")
        return publishers


    async def get_by_id(
        self, db: AsyncSession, publisher_id: int
    ):
        """
        Get publisher by id
        """
        try:
            statement = select(BookPublisher).filter(BookPublisher.id == publisher_id)
            result = await db.execute(statement)           
            publisher = result.scalars().one()
            logging.info(f"Retrieved publisher {publisher_id}.")
            return publisher
        except NoResultFound:
            logging.warning(f"Publisher with id {publisher_id} not found.")
            raise ObjectNotFoundError("Book publisher", publisher_id)
            
        
    async def get_books_by_id(
        self, db: AsyncSession, publisher_id: int
    ):
        """
        Get publisher by id
        """
        # First check if the publisher exists
        publisher_stmt = select(BookPublisher).filter(BookPublisher.id == publisher_id)
        publisher_result = await db.execute(publisher_stmt)
        publisher = publisher_result.scalar_one_or_none()

        if not publisher:
            logging.warning(f"Publisher with id {publisher_id} not found.")
            raise ObjectNotFoundError("Book publisher", publisher_id)
        
        # Publisher exists, now get books
        books_stmt = select(Book).filter(Book.publisher_id == publisher_id).order_by(Book.id)
        books_result = await db.execute(books_stmt)
        books = books_result.scalars().all()
        
        logging.info(f"Retrieved {len(books)} books of publisher {publisher_id}.")
        return books
            

    async def update(
        self, db: AsyncSession, publisher_id, data
    ):
        """
        Update Publisher by id
        """
        statement = select(BookPublisher).filter(BookPublisher.id == publisher_id)

        result = await db.execute(statement)
        publisher = result.scalars().scalar_one_or_none()

        if not publisher:
            logging.warning(f"Publisher {publisher_id} not found.")
            raise ObjectNotFoundError("Book publisher", publisher_id)
        
        publisher.name = data["name"]

        await db.commit()
        await db.refresh(publisher)

        logging.info(f"Successfully updated publisher {publisher_id}.")
        return publisher


    async def delete(self, db: AsyncSession, publisher: BookPublisher):
        """delete publisher by id
        """
        await db.delete(publisher)
        await db.commit()
        await db.refresh(publisher)

        logging.info(f"Successfully deleted publisher {publisher.id}.")
        return {}
       