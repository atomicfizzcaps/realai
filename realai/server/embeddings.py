"""Embedding helpers for the structured RealAI server."""

import logging
from typing import List

from .inference import _build_model
from .logging import log_event
from .metrics import increment


def embed(config, input_texts):
    """Create embeddings for one or more input strings."""
    increment('realai_embedding_requests_total')
    try:
        model = _build_model(config)
        response = model.create_embeddings(
            input_text=input_texts,
            model=config.get('embedding_model', config.get('model_name', 'realai-embeddings')),
        )
        vectors = []
        for item in response.get('data', []):
            vectors.append(item.get('embedding', []))
        log_event(logging.INFO, 'embeddings_created', model=config.get('id'), count=len(vectors))
        return vectors
    except Exception as exc:
        increment('realai_embedding_failures_total')
        log_event(logging.ERROR, 'embeddings_failed', error=str(exc))
        raise
