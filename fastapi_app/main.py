from contextlib import asynccontextmanager

from fastapi import FastAPI

from .database import create_tables
from .routers.catalog import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield


app = FastAPI(title="FastAPI Catalog", lifespan=lifespan)
app.include_router(router)
