from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

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
    
@app.get("/tasks")
def get_tasks():
    return tasks

@app.get("/tasks/{task_id}")
def get_task(task_id:int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    return JSONResponse(
        status_code=404,
        content={"error": f"Task {task_id} not found"}
    )
    
@app.post("/tasks", status_code=201)
def create_task(task_data: CreateTask):
    if task_data.title is None or task_data.title.strip() == "":
        return JSONResponse(
            status_code=404,
            content={"Title is required to create a new task"}
        )
    new_id = max(task['id'] for task in tasks) + 1
    new_task = {
        "id": new_id,
        "title": task_data.title,
        "done": False
    }
    tasks.append(new_task)
    return new_task