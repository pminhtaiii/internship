# Task API

A simple CRUD API built with FastAPI and PostgreSQL.

The application runs with Docker Compose.  
Both the FastAPI application and PostgreSQL database can be started with one command.

## Features

- Create a task
- Get all tasks
- Get a task by ID
- Update a task
- Delete a task
- Store data in PostgreSQL
- Data persists after container restart
- Swagger UI for API testing

## Tech Stack

- Python
- FastAPI
- PostgreSQL
- Psycopg
- Docker
- Docker Compose

## Project Structure

```text
internship/
├── main.py
├── repository.py
├── requirements.txt
├── Dockerfile
├── compose.yaml
├── .env
├── .env.example
├── .gitignore
└── README.md
```

## Environment Variables

Create a `.env` file from `.env.example`.

Example:

```env
DATABASE_URL=postgres://postgres:dev@localhost:5432/tasks
```

The `.env` file is ignored by Git.

## Run with Docker Compose

Start the whole application:

```bash
docker compose up --build
```

After the containers start, open:

```text
http://127.0.0.1:8000/docs
```

To stop the application:

```bash
docker compose down
```

The PostgreSQL data is stored in a Docker volume, so the data remains after stopping and starting the containers again.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/tasks` | Get all tasks |
| GET | `/tasks/{task_id}` | Get a task by ID |
| POST | `/tasks` | Create a new task |
| PUT | `/tasks/{task_id}` | Update a task |
| DELETE | `/tasks/{task_id}` | Delete a task |

## Example

Get all tasks:

```bash
curl -i http://127.0.0.1:8000/tasks
```

Create a task:

```bash
curl -i -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Learn Docker"}'
```

## PostgreSQL

PostgreSQL runs inside a Docker container.

The `tasks` table is created automatically when the application starts.

Three example tasks are added only when the table is empty.

## Persistence

The PostgreSQL service uses a Docker volume.

For example:

1. Create a new task.
2. Run:

```bash
docker compose down
```

3. Start again:

```bash
docker compose up
```

4. Call `GET /tasks`.

The created task is still available because the database data is stored in the Docker volume.

## Database Screenshot

Add a screenshot of the PostgreSQL data here:

```markdown
![Database Screenshot](docs/postgres.png)
```

## Git Ignore

The `.env` file must not be committed to Git.

Example `.gitignore`:

```text
.venv/
__pycache__/
*.pyc
.env
tasks.db
```