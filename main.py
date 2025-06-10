from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1.routers import register_routes
# from library.db.session import engine
# from library.db.models import author, book

# author.Base.metadata.create_all(bind=engine)
# book.Base.metadata.create_all(bind=engine)
        
tags_metadata = [
    {
        "name": "Authentication", 
        "description": "Routes for operations related to Authentication"
    },
    # {
    #     "name": "Book Authors",
    #     "description": "Routes for operations related to authors",
    # },
    # {
    #     "name": "Books",
    #     "description": "Routes for operations related to books",
    # },
]

app = FastAPI(
    title="Books API", 
    description="This is a simple book taking service", 
    version="0.0.1", 
    contact={
        "name": "Ali Sajadian",
        "username": "a.sajadian" 
    } ,
    license_info={
        "name": "MIT"    
    },
    docs_url="/",
    openapi_tags=tags_metadata
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=[]
)

register_routes(app)

