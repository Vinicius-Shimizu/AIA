from fastapi import FastAPI
from todo_app.backend.routes import router as todo_router


app = FastAPI()

if __name__ == "__main__":
    app.include_router(todo_router)