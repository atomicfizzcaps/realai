"""Embedding helpers for the structured RealAI server."""

from realai import RealAI

from .config import get_model_config
from .logging_utils import setup_logging
from .metrics import REQUESTS

logger = setup_logging()
_embed_models = {}


def _get_embed_model(cfg):
    """Load the embedding model lazily."""
    try:
        from sentence_transformers import SentenceTransformer
    except Exception as exc:
        logger.warning('SentenceTransformer unavailable for %s: %s', cfg.get('path'), exc)
        return None

    key = cfg['path']
    if key not in _embed_models:
        logger.info('Loading embedding model: %s', key)
        _embed_models[key] = SentenceTransformer(key)
    return _embed_models[key]


def embed(model_name, texts):
    """Encode texts into embedding vectors."""
    cfg = get_model_config(model_name)
    if cfg['type'] != 'embedding':
        raise ValueError('Model {0} is not embedding type'.format(model_name))
    REQUESTS.labels(endpoint='embeddings', model=model_name).inc()

    model = _get_embed_model(cfg)
    if model is not None:
        vectors = model.encode(texts, convert_to_numpy=True)
        return vectors.tolist()

    fallback = RealAI(model_name=model_name, provider='local', use_local=True)
    response = fallback.create_embeddings(input_text=texts, model=cfg.get('path', model_name))
    return [item.get('embedding', []) for item in response.get('data', [])]
