import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from fastapi_app.database import Base, get_db
from fastapi_app.main import app
from fastapi_app.models import Category, Product  # noqa: F401 — register models

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def db_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine):
    session_factory = async_sessionmaker(db_engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(db_engine):
    session_factory = async_sessionmaker(db_engine, expire_on_commit=False)

    async def override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def seed_data(db_session: AsyncSession):
    electronics = Category(name="Electronics", slug="electronics")
    clothing = Category(name="Clothing", slug="clothing")
    db_session.add_all([electronics, clothing])
    await db_session.flush()

    laptop = Product(name="Laptop Pro", price="1299.99", stock=10, category_id=electronics.id)
    tshirt = Product(name="T-Shirt", price="29.99", stock=100, category_id=clothing.id)
    db_session.add_all([laptop, tshirt])
    await db_session.commit()

    return {"electronics": electronics, "clothing": clothing, "laptop": laptop, "tshirt": tshirt}
