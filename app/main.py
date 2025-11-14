import os

from fastapi import FastAPI
from dotenv import load_dotenv

from app.database import create_db_and_tables
from app.api import router

# Load variables from .env file if present
load_dotenv()

API_TITLE = os.getenv("API_TITLE", "BookStore API")
API_VERSION = os.getenv("API_VERSION", "1.0.0")
ROOT_PATH = os.getenv("ROOT_PATH", "/")  # e.g. /api when behind a proxy


app = FastAPI(
    root_path=ROOT_PATH,
    title=API_TITLE,
    version=API_VERSION,
)


@app.get("/")
def read_root():
    return {
        "message": "Welcome to the FastAPI BookStore application!",
        "root_path": ROOT_PATH,
        "title": API_TITLE,
        "version": API_VERSION,
    }


@app.on_event("startup")
def on_startup():
    """Create tables on startup (development/demo purpose)."""
    create_db_and_tables()


# All book-related endpoints under /api/v1
app.include_router(router, prefix="/api/v1")
