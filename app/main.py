from fastapi import FastAPI

app = FastAPI(title="prompt_optimizer_engine")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
