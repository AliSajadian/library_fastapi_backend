from datetime import timedelta, datetime, timezone
from typing import Annotated
import uuid
import redis.asyncio as redis
from fastapi import Depends, Response
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
import logging
from jose import ExpiredSignatureError, JWTError, jwt

from src.core.config import settings
from ..models import Role, User
from ..schemas import LoginResponse, UserResponse, PasswordChange, Token, RegisterUserRequest
from ..exceptions import AuthenticationError, InvalidPasswordError, PasswordMismatchError, RefreshTokenExpireError, RefreshTokenInvalidError, RefreshTokenMissingError, RefreshTokenTypeInvalidError, UserNotFoundError

# You would want to store this in an environment variable or a secret manager


oauth2_bearer = OAuth2PasswordBearer(tokenUrl='/token')
bcrypt_context = CryptContext(schemes=['bcrypt'], bcrypt__rounds=12)#, deprecated='auto'

class AuthServices:
    """ 
     ==================== 
     Authors API Services 
     ==================== 
    """
    async def register_user(self, db: AsyncSession, register_user_request: RegisterUserRequest) -> User:
        try:
            create_user_model = User(
                username=register_user_request.username,
                first_name=register_user_request.first_name,
                last_name=register_user_request.last_name,
                password_hash=self.__get_password_hash(register_user_request.password)
            )    
            
            db.add(create_user_model)
            await db.commit()
            await db.refresh(create_user_model)
            
            logging.info(f"Created new user.")
            return create_user_model
        
        except Exception as e:
            logging.error(f"Failed to register user: {register_user_request.username}. Error: {str(e)}")
            db.rollback()
            raise
        
    @staticmethod
    def __get_password_hash(password: str) -> str:
        return bcrypt_context.hash(password)

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> UserResponse:
        result = await db.execute(select(User).filter(User.id == user_id)) 
        user = result.scalar_one_or_none()
        
        if not user:
            logging.warning(f"User not found with ID: {user_id}")
            raise UserNotFoundError(user_id)
        
        logging.info(f"Successfully retrieved user with ID: {user_id}")
        return user


    async def change_password(self, db: AsyncSession, user_id: int, password_change: PasswordChange) -> None:
        try:
            user = await self.get_user_by_id(db, user_id)
            
            # Verify current password
            if not self.__verify_password(password_change.current_password, user.password_hash):
                logging.warning(f"Invalid current password provided for user ID: {user_id}")
                raise InvalidPasswordError()
            
            # Verify new passwords match
            if password_change.new_password != password_change.new_password_confirm:
                logging.warning(f"Password mismatch during change attempt for user ID: {user_id}")
                raise PasswordMismatchError()
            
            # Update password
            user.password_hash = self.__get_password_hash(password_change.new_password)
            await db.commit()
            logging.info(f"Successfully changed password for user ID: {user_id}")
        except Exception as e:
            logging.error(f"Error during password change for user ID: {user_id}. Error: {str(e)}")
            raise


    async def login_user(self, db: AsyncSession, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> LoginResponse:
        user = await self.__authenticate_user(db, form_data.username, form_data.password)
        if not user:
            raise AuthenticationError()
        
        # Aggregate permissions from all roles
        # permissions = self.get_permissions(user)
        access_token, _ = self.__create_access_token({
            "sub": str(user.id),
            "roles": [role.name for role in user.roles],
            "permissions": [perm.name for role in user.roles for perm in role.permissions]
        })

        refresh_token, _ = self.__create_refresh_token({
            "sub": str(user.id)
        })
        
        await self.__redis_store_refresh_token(str(user.id), refresh_token)
        
        return LoginResponse(
            user_id=user.id,
            full_name=self.__get_full_name(user),
            access_token=access_token,
            refresh_token=refresh_token,
            # permissions=list(permissions)
        )
    
    @staticmethod
    def get_permissions(user: User):
        permissions = set()
        for role in user.roles:
            for perm in role.permissions:
                permissions.add(perm.name)
        return permissions
    
    @staticmethod
    def __get_full_name(user: User) -> str:
        return f"{user.first_name} {user.last_name}"
                
    async def login_for_access_token(self, form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                    db: AsyncSession) -> Token:
        user = await self.__authenticate_user(db, form_data.username, form_data.password)
        if not user:
            raise AuthenticationError()
        
        token_data = {"sub": user.username, "role": user.role}

        access_token = self.__create_access_token(token_data)
        refresh_token = self.__create_refresh_token(token_data)
        return Token(access_token=access_token, refresh_token=refresh_token, token_type='bearer')
    
    
    async def __authenticate_user(self, db: AsyncSession, username: str, password: str) -> User | bool:
        result = await db.execute(
            select(User)
            .options(selectinload(User.roles).selectinload(Role.permissions))
            .filter(User.username == username))
        user = result.scalar_one_or_none()
        
        if not user or not self.__verify_password(password, user.password_hash):
            logging.warning(f"Failed authentication attempt for username: {username}")
            return False
        return user

    @staticmethod
    def __verify_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt_context.verify(plain_password, hashed_password)


    @staticmethod
    def __create_token(data: dict, expires_delta: timedelta, token_type: str) -> str:
        encode = data.copy()
        token_id = str(uuid.uuid4())
        encode.update({
            'exp': datetime.now(timezone.utc) + expires_delta,
            'jti': token_id,
            "type": token_type
        })
        return jwt.encode(encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM), token_id

    def __create_access_token(self, data: dict):
        return self.__create_token(data, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES), "access")

    def __create_refresh_token(self, data: dict):
        return self.__create_token(data, timedelta(days=settings.REFRESH_EXPIRE_DAYS), "refresh")
    
    
    
    redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

    async def __redis_store_refresh_token(self, user_id: str, token: str):
        key = f"refresh:{user_id}"
        await self.redis_client.set(key, token, ex=60 * 60 * 24 * 7)  # 7 days

    async def __redis_verify_refresh_token(self, user_id: str, token: str) -> bool:
        key = f"refresh:{user_id}"
        stored = await self.redis_client.get(key)
        return stored and stored.decode() == token



    async def refresh_token(self, db: AsyncSession, auth_header: str):
        if not auth_header or not auth_header.startswith("Bearer "):
            raise RefreshTokenMissingError()

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            if payload.get("type") != "refresh":
                raise RefreshTokenTypeInvalidError()
            user_id = payload.get("sub")
        except ExpiredSignatureError:
            raise RefreshTokenExpireError()
        except JWTError:
            raise RefreshTokenInvalidError()

        is_valid = await self.__redis_verify_refresh_token(user_id, token)
        if not is_valid:
            raise RefreshTokenExpireError()

        result = await db.execute(
            select(User)
            .options(selectinload(User.roles).selectinload(Role.permissions))
            .filter(User.id == user_id))
        user = result.scalar_one_or_none()
        
        # Create new access token
        new_access_token = self.__create_access_token(
            user_id=user_id,
            roles=[role.name for role in user.roles],
            permissions=[perm.code for role in user.roles for perm in role.permissions]
        )
        
        return {"access_token": new_access_token, "token_type": "bearer"}


    async def refresh_token_ex(self, db: AsyncSession, token: str):
        if not token:
            raise RefreshTokenMissingError()

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            if payload.get("type") != "refresh":
                raise RefreshTokenTypeInvalidError()
            jti = payload.get("jti")
            user_id = payload.get("sub")
            if not jti or not user_id:
                raise RefreshTokenInvalidError()
            
            redis_user_id = await self.redis_client.get(f"refresh:{jti}")
            if redis_user_id != user_id:
                raise RefreshTokenExpireError()

        except JWTError:
            raise RefreshTokenInvalidError()

        result = await db.execute(
            select(User)
            .options(selectinload(User.roles).selectinload(Role.permissions))
            .filter(User.id == user_id))
        user = result.scalar_one_or_none()
        
        # Create new access token
        new_access_token = self.__create_access_token(
            user_id=user_id,
            roles=[role.name for role in user.roles],
            permissions=[perm.code for role in user.roles for perm in role.permissions]
        )
        
        return {"access_token": new_access_token, "token_type": "bearer"}


    async def logout(self, token: str):
        if token:
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
                jti = payload.get("jti")
                await self.redis_client.delete(f"refresh:{jti}")
            except JWTError:
                pass

        response = Response()
        response.delete_cookie("refresh_token")
        return response
