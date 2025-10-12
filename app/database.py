from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings
import chromadb

SQLALCHEMY_DATABASE_URL = settings.database_url
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)


# Enable foreign key constraint enforcement for SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Lazy loading for ChromaDB to avoid blocking startup
_chroma_client = None
_collection = None


async def get_chroma_client():
    global _chroma_client
    if _chroma_client is None:
        # ChromaDB client initialization with persistent storage
        _chroma_client = chromadb.PersistentClient()
    return _chroma_client


async def get_collection():
    global _collection
    if _collection is None:
        client = await get_chroma_client()
        # Create or get a collection named "tasks"
        _collection = client.get_or_create_collection("tasks")
    return _collection


# For backward compatibility, expose collection as a function call
async def collection():
    return await get_collection()
