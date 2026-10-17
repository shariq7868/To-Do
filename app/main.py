from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, StringConstraints

from app.database import get_connection, init_db

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="My TO_DO", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=FRONTEND_DIR))


class TaskCreate(BaseModel):
    title: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)
    ]


class TaskUpdate(BaseModel):
    completed: bool


class Task(BaseModel):
    id: int
    title: str
    completed: bool


@app.get("/")
def home():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/api/tasks", response_model=list[Task])
def list_tasks():
    with get_connection() as conn:
        return [dict(r) for r in conn.execute("SELECT id, title, completed FROM task")]


@app.post("/api/tasks", response_model=Task)
def create_task(task: TaskCreate):
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO task (title, completed) VALUES (?, 0)", (task.title,)
        )
        return {"id": cursor.lastrowid, "title": task.title, "completed": False}


@app.patch("/api/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task: TaskUpdate):
    with get_connection() as conn:
        cursor = conn.execute(
            "UPDATE task SET completed = ? WHERE id = ?", (task.completed, task_id)
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Task not found")
        row = conn.execute(
            "SELECT id, title, completed FROM task WHERE id = ?", (task_id,)
        ).fetchone()
        return dict(row)


@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int):
    with get_connection() as conn:
        if conn.execute("DELETE FROM task WHERE id = ?", (task_id,)).rowcount == 0:
            raise HTTPException(status_code=404, detail="Task not found")
        return {"detail": "Task deleted"}   