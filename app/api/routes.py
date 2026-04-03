from fastapi import APIRouter

from app.api.schemas import HealthResponse, PromptRequest, PromptResponse, PromptVariant

router = APIRouter()


@router.get("/health")
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.post("/optimize", response_model=PromptResponse)
def optimize(request: PromptRequest) -> PromptResponse:
    return PromptResponse(
        original_prompt=request.prompt,
        variants=[
            PromptVariant(
                type="minimal",
                prompt="Summarize this in one sentence.",
                tokens=12,
                score=70,
            ),
            PromptVariant(
                type="balanced",
                prompt="Summarize this clearly in 2-3 sentences with key details.",
                tokens=24,
                score=84,
            ),
            PromptVariant(
                type="detailed",
                prompt="Summarize this thoroughly with context, key points, and next steps.",
                tokens=42,
                score=92,
            ),
        ],
    )
