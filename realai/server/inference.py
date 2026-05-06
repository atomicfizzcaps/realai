"""Inference helpers for the structured RealAI server."""

import time

from realai import RealAI

from .config import get_model_config
from .logging_utils import setup_logging
from .metrics import LATENCY, REQUESTS, TOKENS

logger = setup_logging()
_vllm_engines = {}


def _build_fallback_model(model_name):
    """Instantiate the legacy RealAI core as a fallback."""
    return RealAI(model_name=model_name, provider='local', use_local=True)


def _get_vllm_engine(cfg):
    """Load a vLLM engine lazily when optional dependencies are available."""
    try:
        from vllm import LLM
    except Exception as exc:
        logger.warning('vLLM unavailable for %s: %s', cfg.get('path'), exc)
        return None

    key = cfg['path']
    if key not in _vllm_engines:
        logger.info('Loading vLLM model: %s', key)
        _vllm_engines[key] = LLM(model=key)
    return _vllm_engines[key]


def chat_completion(model_name, messages, temperature=0.2, max_tokens=1024):
    """Run a chat completion request."""
    cfg = get_model_config(model_name)
    if cfg['type'] != 'chat':
        raise ValueError('Model {0} is not chat type'.format(model_name))

    REQUESTS.labels(endpoint='chat', model=model_name).inc()
    start = time.time()

    prompt = ''
    for message in messages:
        prompt += '{0}: {1}\n'.format(message['role'], message['content'])

    engine = _get_vllm_engine(cfg)
    text = None
    if engine is not None:
        try:
            outputs = engine.generate(
                [prompt],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            text = outputs[0].outputs[0].text
        except Exception as exc:
            logger.warning('vLLM generation failed for %s: %s', model_name, exc)

    if text is None:
        fallback = _build_fallback_model(model_name)
        response = fallback.chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        text = response['choices'][0]['message']['content']

    LATENCY.labels(endpoint='chat', model=model_name).observe(time.time() - start)
    TOKENS.labels(model=model_name, direction='output').inc(len(text.split()))

    return {
        'id': 'chatcmpl-realai',
        'model': model_name,
        'choices': [
            {
                'index': 0,
                'message': {'role': 'assistant', 'content': text},
                'finish_reason': 'stop',
            }
        ],
    }
