from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "prompt_optimizer_engine"
