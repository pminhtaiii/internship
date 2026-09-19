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
    return tasks

@app.get(
    "/tasks/{task_id}",
    summary="Get one task based on task_id",
    description="Return a task by its task id"
)
def get_task(task_id:int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    return JSONResponse(
        status_code=404,
        content={"error": f"Task {task_id} not found"}
    )
    
@app.post(
    "/tasks", status_code=201,
    summary="Create a new task",
    description="Create a new task with a new id, return 404 if the title is None or an empty string"
)
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
    for task in tasks:
        if (task['id'] == task_id):
            if (task_data.title is not None):
                task['title'] = task_data.title
            if (task_data.done is not None):
                task['done'] = task_data.done
            return task
    return JSONResponse(
        status_code=404,
        content={"error": f"Task {task_id} is not found!"}
    )