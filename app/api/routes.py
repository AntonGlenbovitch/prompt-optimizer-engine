from fastapi import APIRouter

from app.api.schemas import (
    AnalyzeResponse,
    BasicOptimizeResponse,
    HealthResponse,
    PromptRequest,
    PromptResponse,
    PromptVariant,
    VariantsResponse,
)
from app.services.analyzer import analyze_prompt
from app.services.optimizer import optimize_prompt
from app.services.tokenizer import estimate_tokens
from app.services.variants import generate_variants

router = APIRouter()


@router.get("/health")
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.post("/optimize", response_model=PromptResponse)
def optimize(request: PromptRequest) -> PromptResponse:
    generated_variants = generate_variants(request.prompt)
    variants = [
        PromptVariant(
            type=variant["type"],
            prompt=variant["prompt"],
            tokens=estimate_tokens(variant["prompt"]),
            score=analyze_prompt(variant["prompt"])["score"],
        )
        for variant in generated_variants
    ]

    return PromptResponse(
        original_prompt=request.prompt,
        variants=variants,
    )


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: PromptRequest) -> AnalyzeResponse:
    result = analyze_prompt(request.prompt)
    return AnalyzeResponse(prompt=request.prompt, score=result["score"], issues=result["issues"])


@router.post("/optimize-basic", response_model=BasicOptimizeResponse)
def optimize_basic(request: PromptRequest) -> BasicOptimizeResponse:
    optimized = optimize_prompt(request.prompt)
    return BasicOptimizeResponse(original=request.prompt, optimized=optimized)


@router.post("/variants", response_model=VariantsResponse)
def variants(request: PromptRequest) -> VariantsResponse:
    return VariantsResponse(original=request.prompt, variants=generate_variants(request.prompt))
