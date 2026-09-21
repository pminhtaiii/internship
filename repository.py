import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_postgres_connection():
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)

def init_postgres():
    conn = get_postgres_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks(
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT FALSE
        )
    """)
    
    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()["count"]
    
    if count == 0:
        cursor.executemany(
            "INSERT INTO tasks (title, done) VALUES (%s, %s)",
            [
                ("learn new knowledge", True),
                ("get a job", False),
                ("become successful", False)
            ]
        )
    
    conn.commit()
    cursor.close()
    conn.close()
    
def get_all_tasks():
    conn = get_postgres_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return tasks
    
def get_task_by_id(task_id):
    conn = get_postgres_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM tasks where id = %s", (task_id,)
    )
    
    task = cursor.fetchone()
    
    cursor.close()
    conn.close()
    return task