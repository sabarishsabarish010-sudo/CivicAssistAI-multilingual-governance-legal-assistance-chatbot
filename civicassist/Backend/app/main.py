from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database.database import create_database
from app.routers import (
    applications,
    chat,
    documents,
    history,
    language,
    legal,
    schemes,
    nearby,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_database()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(chat.router)
app.include_router(schemes.router)
app.include_router(nearby.router)
app.include_router(legal.router)
app.include_router(documents.router)
app.include_router(applications.router)
app.include_router(language.router)
app.include_router(history.router)


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": settings.APP_NAME,
    }