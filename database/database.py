from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import text

from config import DATABASE_URL

engine = create_async_engine(
    url=DATABASE_URL,
    echo=True,
)

session = async_sessionmaker(engine)


async def init_db():
    async with engine.begin() as conn:
        res = await conn.execute(
            text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='feedback'"
            )
        )
        table_exists = res.scalar()

        if not table_exists:
            print("Таблица не найден")
        else:
            print("Таблица найдена")


class Base(DeclarativeBase):
    pass
