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
    
    cursor.execute("SELECT COUNT(*) AS count FROM tasks")
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

def create_task_db(title):
    conn = get_postgres_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """
        INSERT INTO tasks (title, done) 
        VALUES (%s, %s)
        RETURNING *
        """,
        (title, False)
    )
    
    task = cursor.fetchone()
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return task

def update_task_db(task_id, title, done):
    conn = get_postgres_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM tasks WHERE id = %s", (task_id,)
    )
    
    curr_task = cursor.fetchone()
    
    if curr_task is None:
        cursor.close()
        conn.close()
        return None
    
    new_title = title if title is not None else curr_task["title"]
    new_done = done if done is not None else curr_task["done"]
    
    cursor.execute(
        """
        UPDATE tasks
        SET title = %s, done = %s
        WHERE id = %s
        RETURNING *
        """,
        (new_title, new_done, task_id)
    )
    
    updated_task = cursor.fetchone()
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return updated_task

def delete_task_db(task_id):
    conn = get_postgres_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """
        DELETE FROM tasks
        WHERE id = %s
        RETURNING *
        """,
        (task_id,)
    )
    
    deleted_task = cursor.fetchone()
    
    conn.commit()
    cursor.close()
    conn.close()
    return deleted_task
    
    