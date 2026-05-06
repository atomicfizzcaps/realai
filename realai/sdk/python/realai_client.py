"""Python SDK facade for RealAI."""

from realai import RealAI, RealAIClient


__all__ = ['RealAI', 'RealAIClient', 'create_client']


def create_client(api_key=None, provider=None, base_url=None):
    """Create a RealAI client using the OpenAI-compatible interface."""
    return RealAIClient(api_key=api_key, provider=provider, base_url=base_url)
