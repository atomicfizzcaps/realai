"""Embeddings routes."""

from fastapi import APIRouter

from core.api.schemas.embeddings import EmbeddingsRequest, EmbeddingsResponse
from core.models.stub import stub_embeddings

router = APIRouter()


@router.post("/v1/embeddings", response_model=EmbeddingsResponse)
def embeddings(req: EmbeddingsRequest):
    return stub_embeddings(req.input)

