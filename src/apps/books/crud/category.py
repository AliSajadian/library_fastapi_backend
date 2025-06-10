import logging
from uuid import UUID
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from src.apps.books.exceptions import ObjectCreationError, ObjectNotFoundError, ObjectVerificationError
from src.apps.books.models.book import Book
from src.apps.books.models.category import BookCategory
from src.apps.books.schemas.category import CategoryCreate, CategoryUpdate


class CategoryCRUD:
    """ ======================= """
    """ Category API Services """
    """ ======================= """
    async def add(self, db: AsyncSession, category: CategoryCreate):
        try:
            db.add(category)
            await db.commit()
            await db.refresh(category)
            
            logging.info(f"Created new category.")
            return category
        
        except ValidationError as e:
            logging.error(f"Failed to the category data verification. Error: {str(e)}")
            await db.rollback()
            raise ObjectVerificationError("Category", str(e))
        except IntegrityError as e:
            logging.error(f"This category already exists. Error: {str(e)}")
            await db.rollback()
            raise ObjectCreationError("This category already exists.")
        except Exception as e:
            logging.error(f"Failed to create category. Error: {str(e)}")
            await db.rollback()
            raise ObjectCreationError(str(e))


    async def get_all_tree(self, db: AsyncSession, parent_id=None):
        stmt = (
            select(BookCategory)
            .options(
                joinedload(BookCategory.books),
                # joinedload(BookCategory.children)
            )
            .filter(BookCategory.parent_id == parent_id)
        )
        result = await db.execute(stmt)
        categories = result.unique().scalars().all()

        async def build_tree(cat: BookCategory):
            # Recursively fetch children from DB
            child_stmt = (
                select(BookCategory)
                .options(joinedload(BookCategory.books))
                .filter(BookCategory.parent_id == cat.id)
            )
            child_result = await db.execute(child_stmt)
            children = child_result.unique().scalars().all()
            return {
                "id": cat.id,
                "name": cat.name,
                "parent_id": cat.parent_id,
                "books": [
                    {"id": book.id, "title": book.title} for book in cat.books
                ],
                "children": [await build_tree(child) for child in children],
            }

        return [await build_tree(cat) for cat in categories]


    async def get_by_id(self, db: AsyncSession, category_id: UUID):
        stmt = select(BookCategory).where(BookCategory.id == category_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()


    async def get_books_by_id(
        self, db: AsyncSession, category_id: UUID
    ):
        """
        Get books by category id
        """
        # First check if the category exists
        category_stmt = select(BookCategory).filter(BookCategory.id == category_id)
        category_result = await db.execute(category_stmt)
        category = category_result.scalar_one_or_none()

        if not category:
            logging.warning(f"Category with id {category_id} not found.")
            raise ObjectNotFoundError("Category", category_id)
        
        # Author exists, now get books
        books_stmt = select(Book).filter(Book.category_id == category_id).order_by(Book.id)
        books_result = await db.execute(books_stmt)
        books = books_result.scalars().all()
        
        logging.info(f"Retrieved {len(books)} books of category {category_id}.")
        return books
            

    async def update(self, db: AsyncSession, category_id: UUID, data: CategoryUpdate):
        category = await self.get_category(db, category_id)
        if not category:
            return None
        for key, value in data.dict(exclude_unset=True).items():
            setattr(category, key, value)
        await db.commit()
        await db.refresh(category)
        return category


    async def delete(self, db: AsyncSession, category_id: UUID):
        category = await self.get_category(db, category_id)
        if category:
            await db.delete(category)
            await db.commit()
        return category
