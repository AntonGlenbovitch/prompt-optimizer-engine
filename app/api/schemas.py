from typing import List

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class PromptRequest(BaseModel):
    prompt: str


class PromptVariant(BaseModel):
    type: str
    prompt: str
    tokens: int
    score: int
    issues: List[str]


class PromptResponse(BaseModel):
    original_prompt: str
    variants: List[PromptVariant]
    comparison: dict[str, int]


class AnalyzeResponse(BaseModel):
    prompt: str
    score: int
    issues: List[str]


class BasicOptimizeResponse(BaseModel):
    original: str
    optimized: str


class VariantsResponse(BaseModel):
    original: str
    variants: List[dict]
