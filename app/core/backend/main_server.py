from fastapi import FastAPI
from todo_app.backend import register as registerTodo
from stt import STTEngine
from contextlib import asynccontextmanager
import asyncio
from ollama_client.model import Model
stt = None
model = None
mcp = None
event_queue = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global stt, model, mcp

    # mcp = FastMCP("AIA MCP Server")
    # registerAll(mcp)
    # model = await Model.create(mcp_instance=mcp)
    app.state.model = await Model.create(mcp_instance=mcp)
    
    app.state.event_queue = asyncio.Queue()
    loop = asyncio.get_running_loop()
    stt = STTEngine(event_queue=app.state.event_queue, loop=loop)
    stt.start()
    worker = asyncio.create_task(eventWorker(app))
    yield
    stt.stop()
    worker.cancel() 
    try:
        await worker
    except asyncio.CancelledError:
        pass

async def eventWorker(app):
    queue = app.state.event_queue
    try:
        while True:
            event = await queue.get()
            print("Event: ", event)

            if event["status"] == "transcripted":
                response = await app.state.model.handleQuery(event["message"])
                print(response)
    except asyncio.CancelledError:
        raise "Event worker shutting down"


app = FastAPI(lifespan=lifespan)
registerTodo(app)
