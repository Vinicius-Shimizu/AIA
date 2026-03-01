from .routes import router
from .db import init_schema

def register(app):
    init_schema()
    app.include_router(router)