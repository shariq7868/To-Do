from contextlib import asynccontextmanager
from pathlib import Path
import sqlite3

from fastapi import FastAPI,HTTPException,status
from fastapi.responses import FileResponse
from fastapi.staticfile import StaticFiles
from pydantic import BaseModel,Field

from app.database import get_connection,init_db

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

@asynccontextmanager
async def lifspan(app:FastAPI):
    init_db()
    yield

app = FastAPI(
    title="My To-Do",
    version="1.0.0",
    lifspan=lifspan,
)

app.mount(
    "/static",
    StaticFiles(directory=str(FRONTEND_DIR)),
    name="Static",
)

class TaskCreate(BaseModel):
    title: str = Field(min_length=1,max_length=200)

class TaskUpdate(BaseModel):
    completed: bool

def serialize_task(row: sqlite3.Row) -> dict:
    return{
        "id":row[id],
        "title":row["title"],
        "completed":bool(row["completed"]),
    }

@app.get("/")
def home():
    return FileResponse(FRONTEND_DIR/"index.html")

@app.get("/api/tasks")
def get_task():
    with get_connection() as connection:
        rows = connection.execute(
            "Select id, title, Complete From task"
        ).fetchall()
    return [serialize_task(row) for row in rows]