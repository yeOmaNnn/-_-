import asyncio
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from data.config import DATABASE_URL
from models import Base

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_session_async() -> AsyncSession:
    async with async_session() as session:
        yield session

async def init_models():
    async with engine.begin() as conn:
        try:
            await conn.run_sync(Base.metadata.create_all)

        except Exception as e:
            print(e)

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_models())


if __name__ == "__main__":
    main()