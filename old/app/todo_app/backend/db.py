import psycopg
from dotenv import load_dotenv
import os

load_dotenv()
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

def get_connection():
    return psycopg.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

def init_schema():
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
        conn.commit()