from fastapi import FastAPI
from routes import router as todo_router
from contextlib import asynccontextmanager
from db import get_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                        DO $$
                        BEGIN
                            CREATE TYPE priority_enum AS ENUM ('LOW', 'MEDIUM', 'HIGH');
                        EXCEPTION
                            WHEN duplicate_object THEN NULL;
                        END $$
                        """)
            cur.execute("""
                        DO $$
                        BEGIN
                            CREATE TYPE status_enum AS ENUM ('to-do', 'in-progress', 'done');
                        EXCEPTION
                            WHEN duplicate_object THEN NULL;
                        END $$
                        """)
            cur.execute("""
                        CREATE TABLE IF NOT EXISTS todos (
                            id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                            name TEXT NOT NULL,
                            description TEXT NOT NULL,
                            priority priority_enum NOT NULL DEFAULT 'LOW',
                            status status_enum NOT NULL DEFAULT 'to-do'
                        )
                        """)
        conn.commit()  # ← critical
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(todo_router)