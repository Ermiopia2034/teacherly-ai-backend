from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Define the database URL from settings
DATABASE_URL = settings.DATABASE_URL

# Create an asynchronous engine
engine = create_async_engine(DATABASE_URL, echo=True) # echo=True for logging SQL, remove in production

# Create a session maker
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Create a base for declarative models
Base = declarative_base()

# Dependency to get a DB session
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit() # Commit changes if no exceptions
        except Exception:
            await session.rollback() # Rollback on error
            raise
        finally:
            await session.close()