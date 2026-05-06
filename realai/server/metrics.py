"""Prometheus-style in-memory metrics for the RealAI server."""

from collections import defaultdict
from threading import Lock

_COUNTERS = defaultdict(int)
_LOCK = Lock()


def increment(name, value=1):
    """Increment an in-memory counter."""
    with _LOCK:
        _COUNTERS[name] += value
        return _COUNTERS[name]


def snapshot():
    """Return a copy of current counters."""
    with _LOCK:
        return dict(_COUNTERS)


def render_prometheus_text():
    """Render metrics in Prometheus text format."""
    lines = []
    for name in sorted(snapshot()):
        lines.append('# TYPE {0} counter'.format(name))
        lines.append('{0} {1}'.format(name, snapshot()[name]))
    return '
'.join(lines) + ('
' if lines else '')
