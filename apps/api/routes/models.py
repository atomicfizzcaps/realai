"""Model routes."""

from fastapi import APIRouter

from core.api.schemas.models import ModelsListResponse
from core.models.registry import ModelRegistry

router = APIRouter()


@router.get("/v1/models", response_model=ModelsListResponse)
def list_models():
    return {"data": ModelRegistry().list_models()}

