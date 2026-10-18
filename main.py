
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import mysql.connector

app = FastAPI(title="Task Management API")


# MySQL database connection
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="jagan@2002",
        database="task_management"
    )


# Pydantic model
class Task(BaseModel):
    title: str
    description: str = ""
    completed: bool = False


# CREATE a task
@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task: Task):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO tasks (title, description, completed) VALUES (%s, %s, %s)",
        (task.title, task.description, task.completed)
    )

    connection.commit()
    task_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return {"id": task_id, **task.model_dump()}


# READ all tasks
@app.get("/tasks")
def get_tasks():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()

    cursor.close()
    connection.close()

    return tasks


# READ one task
@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    task = cursor.fetchone()

    cursor.close()
    connection.close()

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


# UPDATE a task
@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: Task):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """UPDATE tasks
           SET title = %s, description = %s, completed = %s
           WHERE id = %s""",
        (task.title, task.description, task.completed, task_id)
    )

    if cursor.rowcount == 0:
        cursor.execute("SELECT id FROM tasks WHERE id = %s", (task_id,))
        if cursor.fetchone() is None:
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="Task not found")

    connection.commit()
    cursor.close()
    connection.close()

    return {"message": "Task updated successfully"}


# DELETE a task
@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))

    if cursor.rowcount == 0:
        cursor.close()
        connection.close()
        raise HTTPException(status_code=404, detail="Task not found")

    connection.commit()
    cursor.close()
    connection.close()
