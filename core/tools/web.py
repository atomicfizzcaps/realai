"""Web search tool."""

from typing import Any, Dict

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None

from core.tools.base import Tool


class WebSearchTool(Tool):
    name = "web_search"
    description = "Search the web"
    params_schema = {"query": {"type": "string"}}
    permissions = ["network"]

    def __call__(self, **kwargs: Any) -> Dict[str, Any]:
        query = str(kwargs.get("query", "")).strip()
        if not query:
            return {"results": [], "query": query}
        if requests is None:
            return {"results": ["requests unavailable in runtime"], "query": query}
        try:
            response = requests.get(
                "https://duckduckgo.com/html/",
                params={"q": query},
                timeout=5,
                headers={"User-Agent": "realai-tool/1.0"},
            )
            text = response.text[:500]
            return {"results": [text], "query": query}
        except Exception as exc:
            return {"results": [], "query": query, "error": str(exc)}

