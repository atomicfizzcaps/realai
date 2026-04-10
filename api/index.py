"""
Vercel serverless entry point for RealAI.

Vercel's Python runtime looks for a ``handler`` symbol in files under the
``api/`` directory.  We simply re-export :class:`~api_server.RealAIAPIHandler`
(which already extends :class:`~http.server.BaseHTTPRequestHandler`) under the
name ``handler`` so Vercel can dispatch HTTP requests to it.

All routing logic (including the web UI at ``/`` and the JSON API at
``/v1/chat/completions`` etc.) is implemented in ``api_server.py``.
"""

import sys
import os

# Make sure the project root is on the path so that
# ``import api_server`` and ``import realai`` resolve correctly.
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from api_server import RealAIAPIHandler as handler  # noqa: F401  (re-exported for Vercel)
