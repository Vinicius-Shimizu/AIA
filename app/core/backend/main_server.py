from fastapi import FastAPI
from todo_app.backend import register as registerTodo
from stt import setup as sttSetup
from contextlib import asynccontextmanager

stt = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global stt
    stt = sttSetup(app)
    stt.start()
    yield
    stt.stop()


app = FastAPI(lifespan=lifespan)
registerTodo(app)