from fastapi import FastAPI
from src.apps.auth.routers import auth_routers, permission_routers, role_routers, user_routers
from src.apps.books.routers import author_routers, book_routers, category_routers, publisher_routers


def register_routes(app: FastAPI):
    app.include_router(auth_routers, prefix="/api/v1/auth", tags=["Authentication"])
    app.include_router(user_routers, prefix="/api/v1/auth/user", tags=["Users"])
    app.include_router(role_routers, prefix="/api/v1/auth/role", tags=["Roles"])
    app.include_router(permission_routers, prefix="/api/v1/auth/permission", tags=["Permissions"])

    app.include_router(author_routers, prefix="/api/v1/author", tags=["Book Authors"])
    app.include_router(category_routers, prefix="/api/v1/category", tags=["Book Categories"])
    app.include_router(publisher_routers, prefix="/api/v1/publisher", tags=["Book Publishers"])
    app.include_router(book_routers, prefix="/api/v1/book", tags=["Books"])
    
    
