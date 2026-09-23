from fastapi import FastAPI, Response, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from repository import (
    init_postgres,
    get_all_tasks,
    get_task_by_id,
    create_task_db,
    update_task_db,
    delete_task_db
)
from auth import supabase
    
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
    
    return create_task_db(task_data.title)

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
    
    task = update_task_db(task_id, task_data.title, task_data.done)
    
    if task is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"Task {task_id} is not found!"}
        )
        
    return task
    
@app.delete(
    "/tasks/{task_id}",
    status_code=204,
    summary="Delete a task",
    description="Delete a task based on task_id"
)
def delete_task(task_id: int):
    deleted_task = delete_task_db(task_id)
    
    if deleted_task is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"Task {task_id} is not found!"}
        )
    return deleted_task

@app.post(
    "/public/info",
    summary="Public information",
    description="This endpoint can be accessed without authentication"
)
def public_info():
    return {"message": "Welcome stranger! This info is public."}

@app.post(
    "/protected/profile",
    summary="Protected information",
    description="This profile is only be accessed by authenticated users"
)
def protected_profile(authorization: str | None = Header(default=None)):
    if authorization is None:
        return JSONResponse(
            status_code=401,
            content={"error": "Access token required"}
        )
    if not authorization.startswith("Bearer "):
        return JSONResponse(
            status_code=401,
            content={"error": "Access token required"}
        )
    token = authorization.removeprefix("Bearer ").strip()
    
    if token == "":
        return JSONResponse(
            status_code=401,
            content={"error": "Access token required"}
        )
        
    return {
        "message": "Token received",
        "token": token
    }