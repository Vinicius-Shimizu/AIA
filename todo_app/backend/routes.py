from typing import List
from fastapi import APIRouter, HTTPException
from schemas import TodoCreate, Todo, TodoBase, Priority, Status
from db import get_connection

router = APIRouter(prefix="/todos")

@router.get('/all', response_model=List[Todo])
def get_all_todos():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, name, description, priority, status
                FROM todos            
                ORDER by id;
            """)
            rows = cur.fetchall()
    
    return [
        Todo(
            id=r[0],
            name=r[1],
            description=r[2],
            priority=Priority(r[3]),
            status=Status(r[4]),
        )
        for r in rows
    ]


@router.get('/{id}', response_model=Todo)
def get_todo_info(id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT id, name, description, priority, status
                FROM todos            
                WHERE id = %s;
            """, (id,))
            row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return Todo(
        id=row[0],
        name=row[1],
        description=row[2],
        priority=Priority(row[3]),
        status=Status(row[4]),
    )
        
    
@router.post('/', response_model=Todo)
def create_todo(todo: TodoCreate):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                        INSERT INTO todos (name, description, priority, status) 
                        VALUES (%s, %s, %s, %s)
                        RETURNING id, name, description, priority, status;
                        """, (todo.name, todo.description, todo.priority.name, todo.status.value))
            row = cur.fetchone()
    return Todo(
        id=row[0],
        name=todo.name,
        description=todo.description,
        priority=todo.priority,
        status=todo.status,
    )
    
@router.put('/todos/{id}', response_model=Todo)
def update_todo(id: int, updated_todo: TodoBase):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                        UPDATE todos
                        SET name = %s,
                            description = %s,
                            priority = %s,
                            status = %s
                        WHERE id = %s
                        RETURNING id, name, description, priority, status;
                        """, (updated_todo.name, updated_todo.description, updated_todo.priority.name, updated_todo.status.value, id))
            row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    return Todo(
        id=row[0],
        name = updated_todo.name,
        description=updated_todo.description,
        priority=updated_todo.priority,
        status=updated_todo.status
    )

@router.delete('/todos/{id}', response_model=Todo)
def delete_todo(id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                        DELETE FROM todos
                        WHERE id = %s
                        RETURNING id, name, description, priority, status;
                        """, (id,))
            row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    return Todo(
        id=row[0],
        name=row[1],
        description=row[2],
        priority=Priority(row[3]),
        status=Status(row[4]),
    )