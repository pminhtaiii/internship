from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from repository import (
    init_postgres,
    get_all_tasks,
    get_task_by_id
)
import sqlite3

DATABASE = "tasks.db"

def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0
        )               
    """)
    
    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]
    
    if count == 0:
        cursor.executemany(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            [
                ("learn new knowledge", 1),
                ("get a job", 0),
                ("become successful", 0)
            ]
        )
    
    conn.commit()
    conn.close()
    
init_db()

def row_to_task(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"])
    }
    
init_postgres()

app = FastAPI()

tasks = [
    {
        "id": 1,
        "title": "learn new knowledge",
        "done": True
    },
    {
        "id": 2,
        "title": "get a job",
        "done": False
    },
    {
        "id": 3,
        "title": "become successful",
        "done": False
    },
]

class CreateTask(BaseModel):
    title: str | None = None
    
class UpdateTask(BaseModel):
    title: str | None = None
    done: bool | None = None

@app.get("/")
def root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }
    
@app.get("/health")
def health():
    return {
        "status": "ok"
    }
    
@app.get(
    "/tasks",
    summary="Get all the tasks available",
    description="Return all tasks in memory"
)
def get_tasks():
    return get_all_tasks()

@app.get(
    "/tasks/{task_id}",
    summary="Get one task based on task_id",
    description="Return a task by its task id"
)
def get_task(task_id:int):
    task = get_task_by_id(task_id)
    
    if task is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"Task {task_id} is not found!"}
        )
    return task

@app.post(
    "/tasks", status_code=201,
    summary="Create a new task",
    description="Create a new task with a new id, return 400 if the title is None or an empty string"
)
def create_task(task_data: CreateTask):
    if task_data.title is None or task_data.title.strip() == "":
        return JSONResponse(
            status_code=400,
            content={"error": "Title is required to create a new task!"}
        )
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        (task_data.title, 0)
    )
    
    new_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    
    new_task = {
        "id": new_id,
        "title": task_data.title,
        "done": False
    }
    
    return new_task

@app.put(
    "/tasks/{task_id}",
    summary="Update a task",
    description="Update a task with a new payload"
)
def update_task(task_id: int, task_data: UpdateTask):
    if task_data.title is None and task_data.done is None:
        return JSONResponse(
            status_code=400,
            content={"error": "At least one type of content is needed to update"}
        )
    if task_data.title is not None and task_data.title.strip() == "":
        return JSONResponse(
            status_code=400,
            content={"error": "A title can not be an empty string!"}
        )
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    )
    
    row = cursor.fetchone()
    
    if row is None:
        conn.close()
        return JSONResponse(
            status_code=404,
            content={"error": f"Task {task_id} is not found!"}
        )
    
    new_title = (
        task_data.title
        if task_data.title is not None
        else row['title']
    )
    
    new_done = (
        task_data.done
        if task_data.done is not None
        else row['done']
    )
    
    cursor.execute(
        """
        UPDATE tasks
        SET title = ?, done = ?
        WHERE id = ?
        """,
        (new_title, new_done, task_id)
    )
    
    conn.commit()
    conn.close()
    
    return {
        "id": task_id,  
        "title": new_title,
        "done": new_done
    }
    
@app.delete(
    "/tasks/{task_id}",
    status_code=204,
    summary="Delete a task",
    description="Delete a task based on task_id"
)
def delete_task(task_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "DELETE FROM tasks WHERE id = ?",
        (task_id,)
    )
    
    if cursor.rowcount == 0:
        conn.close()
        return JSONResponse(
            status_code=404,
            content={"error": f"Task {task_id} is not found!"}
        )
    
    conn.commit()
    conn.close()
    
    return Response(status_code=204)