from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(title="prompt_optimizer_engine")
app.include_router(router)
