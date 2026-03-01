from .stt_engine import STTEngine
from .routes import router

stt = STTEngine()

def setup(app):
    app.include_router(router)
    return stt