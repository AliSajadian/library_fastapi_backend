from sqlalchemy import MetaData#, create_engine
from sqlalchemy.orm import declarative_base# sessionmaker, 
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine

from src.core.config import settings

# engine = create_engine(url=settings.DATABASE_URL, echo=True, future=True)

async_engine = create_async_engine(url=settings.ASYNC_DATABASE_URL, echo=True, future=True)

# SessionLocal = sessionmaker(
#     autocommit=False,
#     autoflush=False,
#     bind=engine,
#     future=True
# )

AsyncSessionLocal = async_sessionmaker(
    async_engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

Base = declarative_base()

#CORE
# Metadata = MetaData()
# Metadata.reflect(bind=async_engine)

# stmt = select(users_table).where(users_table.c.username == "admin")
# with engine.connect() as conn:
#     result = conn.execute(stmt)
#     rows = result.fetchall()

#ORM
# Your ORM model
# class User(Base):
#     __tablename__ = "users"
#     id = Column(Integer, primary_key=True)
#     username = Column(String)
# Manual mapping
# table_model_map = {
#     "users": User,
#     # Add more mappings if needed
# }

# model = table_model_map.get("users")
# stmt = select(model).where(model.username == "admin")
