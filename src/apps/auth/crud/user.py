import logging
from passlib.context import CryptContext
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.auth.schemas.role import RoleModel
from src.apps.auth.schemas.user import UserCreateModel, UserModel
from src.apps.auth.services.auth import AuthServices
from ..models import User, Role
from src.apps.books.exceptions import ObjectCreationError, ObjectVerificationError, ObjectNotFoundError


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserCRUDs:
    """ ================== """
    """ Users API Services """
    """ ================== """ 
    def __get_password_hash(self, password: str) -> str:
        return bcrypt_context.hash(password)


    async def add(self, db: AsyncSession, user_data: UserCreateModel):
        """
        Create role object
        """
        try:
            user = User(
                username=user_data.username, 
                first_name=user_data.first_name, 
                last_name=user_data.last_name, 
                password_hash=self.__get_password_hash(user_data.password)
            )
            
            role_ids=user_data.role_ids
            
            db.add(user)
            # await db.flush()        
            
            if role_ids:
                roles_result = await db.execute(
                    select(Role).where(Role.id.in_(role_ids))
                )
                roles = roles_result.scalars().all()
                # Now reload the role from the session to ensure it's attached
                statement = select(User).where(User.id == user.id)

                result = await db.execute(statement)
                attached_user = result.scalars().first()
                attached_user.roles = roles

                # Use attached_role for further operations
                await db.commit()
                await db.refresh(attached_user)

                # Eagerly load roles
                statement = (
                    select(User)
                    .options(selectinload(User.roles))
                    .where(User.id == attached_user.id)
                )

                result = await db.execute(statement)
                user_with_roles = result.scalars().first()
            else:

                await db.commit()
                await db.refresh(user)
                # Eagerly load roles
                statement = (
                    select(User)
                    .options(selectinload(User.roles))
                    .where(User.id == user.id)
                )

                result = await db.execute(statement)
                user_with_roles = result.scalars().first()

            # Force loading all role fields (no lazy loading later)
            _ = [p.id for p in user_with_roles.roles]
        
            logging.info(f"Created new user.")
            
            for p in user_with_roles.roles:
                print(f"Role: id={p.id}, name={p.name}, description={p.description}")
                
            # return RoleModel.model_validate(role_with_roles)
            # roles_data = [
            #     # PermissionModel.model_validate(p) 
            #     {
            #         "id": str(p.id),
            #         "name": p.name,
            #         "description": p.description
            #     }
            #     for p in user_with_roles.roles
            #     # PermissionModel(id=p.id, name=p.name, description=p.description)
            #     # for p in role_with_roles.roles
            # ]
            roles_data = [
                RoleModel(
                    id=p.id,
                    name=p.name,
                    description=p.description
                )
                for p in user_with_roles.roles
            ]
            user_data = {
                "id": str(user_with_roles.id),
                "first_name": user_with_roles.first_name,
                "last_name": user_with_roles.last_name,
                "username": user_with_roles.username,
                # "password_hash": user_with_roles.password_hash,
                "roles": roles_data
            }
            return UserModel(**user_data)
            # return RoleModel(**user_data)


        except ValidationError as e:
            logging.error(f"Failed to the user data verification. Error: {str(e)}")
            await db.rollback()
            raise ObjectVerificationError("User", str(e))
        except IntegrityError as e:
            logging.error(f"Username already exists. Error: {str(e)}")
            await db.rollback()
            raise ObjectCreationError("Username already exists.")
        except Exception as e:
            logging.error(f"Failed to create user. Error: {str(e)}")
            await db.rollback()
            raise ObjectCreationError(str(e))
    

    async def add1(self, db: AsyncSession, user: User):
        """
        Create user object
        """
        try:
            db.add(user)
            await db.commit()
            await db.refresh(user)
            
            logging.info(f"Created new user.")
            return user
    
        except ValidationError as e:
            logging.error(f"Failed to the user data verification. Error: {str(e)}")
            await db.rollback()
            raise ObjectVerificationError(str(e))
        except Exception as e:
            logging.error(f"Failed to create user. Error: {str(e)}")
            await db.rollback()
            raise ObjectCreationError(str(e))        


    async def get_all(self, db: AsyncSession):
        """
        Get all users objects from db
        """
        statement = select(User).order_by(User.id)

        result = await db.execute(statement)
        users = result.scalars().all()
        
        logging.info(f"Retrieved {len(users)} users.")
        return users


    async def get_by_id(
        self, db: AsyncSession, user_id: int
    ):
        """
        Get user by id
        """
        try:
            statement = select(User).filter(User.id == user_id)
            result = await db.execute(statement)           
            user = result.scalars().one()
            logging.info(f"Retrieved user {user_id}.")
            return user
        except NoResultFound:
            logging.warning(f"User with id {user_id} not found.")
            raise ObjectNotFoundError(user_id)
            
        
    async def get_roles_by_user_id(
        self, db: AsyncSession, user_id: int
    ):
        """
        Get user by id
        """
        # First check if the user exists
        user_stmt = select(User).filter(User.id == user_id)
        user_result = await db.execute(user_stmt)
        user = user_result.scalar_one_or_none()

        if not user:
            logging.warning(f"User with id {user_id} not found.")
            raise ObjectNotFoundError(user_id)
        
        # User exists, now get roles
        roles_result = await db.execute(
                    select(Role)
                    .options(selectinload(User.roles))
                    .filter(Role.user_id == user_id)
                    .order_by(Role.id))
        roles = roles_result.scalars().all()
        
        logging.info(f"Retrieved {len(roles)} roles of user {user_id}.")
        return roles
            

    async def get_permissions_by_user_id(
        self, db: AsyncSession, user_id: int
    ):
        """
        Get user by id
        """
        # First check if the user exists
        result = await db.execute(
            select(User)
            .options(selectinload(User.roles).selectinload(Role.permissions))
            .filter(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            logging.warning(f"User with id {user_id} not found.")
            raise ObjectNotFoundError(user_id)
        
        # User exists, now get permissions
        permissions = AuthServices().get_permissions(user)
        
        logging.info(f"Retrieved {len(permissions)} roles of user {user_id}.")
        return permissions


    async def update(
        self, db: AsyncSession, user_id, data
    ):
        """
        Update User by id
        """
        statement = select(User).filter(User.id == user_id)

        result = await db.execute(statement)
        user = result.scalars().scalar_one_or_none()

        if not user:
            logging.warning(f"User {user_id} not found.")
            raise ObjectNotFoundError(user_id)
        
        user.name = data["name"]
        user.username = data["username"]

        await db.commit()
        await db.refresh(user)

        logging.info(f"Successfully updated user {user_id}.")
        return user


    async def delete(self, db: AsyncSession, user: User):
        """delete user by id
        """
        await db.delete(user)
        await db.commit()
        await db.refresh(user)

        logging.info(f"Successfully deleted user {user.id}.")
        return {}
       