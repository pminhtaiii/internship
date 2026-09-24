from fastapi import FastAPI, Response, Depends
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
from auth import supabase, get_current_user
    
init_postgres()

app = FastAPI()

class CreateTask(BaseModel):
    title: str | None = None
    
class UpdateTask(BaseModel):
    title: str | None = None
    done: bool | None = None
    
class AuthData(BaseModel):
    email: str | None = None
    password: str | None = None

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
    description="Return all tasks from PostgresSQL"
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
    return Response(status_code=204)

@app.post(
    "/auth/signup",
    status_code=201,
    summary="Sign up",
    description="Sign up as a new user with email and password"
)
def signup(auth_data: AuthData):
    if auth_data.email is None or auth_data.password is None or auth_data.email.strip() == "" or auth_data.password.strip() == "":
        return JSONResponse(
            status_code=400,
            content={"error": "Email and password are required to sign up!"}
        )
    try:
        response = supabase.auth.sign_up({
            "email": auth_data.email,
            "password": auth_data.password
        })
        return {
            "id": str(response.user.id),
            "email": response.user.email
        }
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"error": "An error occurred while signing up"}
        )
    
@app.post(
    "/auth/login",
    summary="Login",
    description="Login a user with an existed account"
)
def login(auth_data: AuthData):
    if auth_data.email is None or auth_data.password is None or auth_data.email.strip() == "" or auth_data.password.strip() == "":
        return JSONResponse(
            status_code=400,
            content={"error": "Email and password are required to login!"}
        )
    try:
        response = supabase.auth.sign_in_with_password({
            "email": auth_data.email,
            "password": auth_data.password
        })
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token
        }
    except Exception as e:
        return JSONResponse(
            status_code=401,
            content={"error": "Invalid login credentials"}
        )

@app.get(
    "/public/info",
    summary="Public information",
    description="This endpoint can be accessed without authentication"
)
def public_info():
    return {"message": "Welcome stranger! This info is public."}

@app.get(
    "/protected/profile",
    summary="Protected information",
    description="This profile is only be accessed by authenticated users"
)
def protected_profile(current_user = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "created_at": str(current_user.created_at)
    }

@app.get(
    "protected/dashboard",
    summary="Protected dashboard",
    description="The dashboard for authenticated users"
)
def protected_dashboard(current_user = Depends(get_current_user)):
    return {
        "message": "Welcome to our dashboard",
        "user_id": str(current_user.id),
        "email": current_user.email
    }
    
@app.post(
    "/auth/logout",
    summary="Logout",
    status_code=204
)
def logout(current_user = Depends(get_current_user)):
    try:
        supabase.auth.sign_out()
        return Response(status_code=204)
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"error": "Log out failed!"}
        )