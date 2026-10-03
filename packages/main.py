from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.gzip import GZipMiddleware

from packages.database import engine
from packages.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Ticket Classification System",
        debug=settings.DEBUG,
        lifespan=lifespan,
        middleware=[Middleware(GZipMiddleware)],
    )
    return app


app = create_app()
