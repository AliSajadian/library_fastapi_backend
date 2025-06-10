from fastapi import HTTPException

class BookError(HTTPException):
    """Base exception for book-related errors"""
    pass

class BookNotFoundError(BookError):
    def __init__(self, book_id=None):
        message = "Book not found" if book_id is None else f"Book with id {book_id} not found"
        super().__init__(status_code=404, detail=message)

class BookCreationError(BookError):
    def __init__(self, error: str):
        super().__init__(status_code=500, detail=f"Failed to create book: {error}")

class UserError(HTTPException):
    """Base exception for user-related errors"""
    pass

class UserNotFoundError(UserError):
    def __init__(self, user_id=None):
        message = "User not found" if user_id is None else f"User with id {user_id} not found"
        super().__init__(status_code=404, detail=message)

class UserCreationError(UserError):
    def __init__(self, error: str):
        super().__init__(status_code=500, detail=f"Failed to create user: {error}")
        
class UserVerificationError(UserError):
    def __init__(self, error: str):
        super().__init__(status_code=422, detail=f"Failed to the user data verification: {error}")
        
        
class RoleError(HTTPException):
    """Base exception for role-related errors"""
    pass

class RoleNotFoundError(RoleError):
    def __init__(self, role_id=None):
        message = "Role not found" if role_id is None else f"Role with id {role_id} not found"
        super().__init__(status_code=404, detail=message)

class RoleCreationError(RoleError):
    def __init__(self, error: str):
        super().__init__(status_code=500, detail=f"Failed to create role: {error}")
        
        
class RoleVerificationError(RoleError):
    def __init__(self, error: str):
        super().__init__(status_code=422, detail=f"Failed to the role data verification: {error}")


class PermissionError(HTTPException):
    """Base exception for permission-related errors"""
    pass

class PermissionNotFoundError(PermissionError):
    def __init__(self, permission_id=None):
        message = "Permission not found" if permission_id is None else f"Permission with id {permission_id} not found"
        super().__init__(status_code=404, detail=message)

class PermissionCreationError(PermissionError):
    def __init__(self, error: str):
        super().__init__(status_code=500, detail=f"Failed to create permission: {error}")

class PermissionVerificationError(PermissionError):
    def __init__(self, error: str):
        super().__init__(status_code=422, detail=f"Failed to the permission data verification: {error}")


class PasswordMismatchError(UserError):
    def __init__(self):
        super().__init__(status_code=400, detail="New passwords do not match")

class InvalidPasswordError(UserError):
    def __init__(self):
        super().__init__(status_code=401, detail="Current password is incorrect")

class AuthenticationError(HTTPException):
    def __init__(self, message: str = "Could not validate user"):
        super().__init__(status_code=401, detail=message)


class RefreshTokenMissingError(HTTPException):
    def __init__(self, message: str = "Refresh token missing"):
        super().__init__(status_code=401, detail=message)
        
class RefreshTokenTypeInvalidError(HTTPException):
    def __init__(self, message: str = "Invalid token type"):
        super().__init__(status_code=403, detail=message)

class RefreshTokenInvalidError(HTTPException):
    def __init__(self, message: str = "Invalid refresh token"):
        super().__init__(status_code=403, detail=message)
        
class RefreshTokenExpireError(HTTPException):
    def __init__(self, message: str = "Token expired or revoked"):
        super().__init__(status_code=403, detail=message)
        
