"""Structured RealAI inference server."""

import json
from wsgiref.simple_server import make_server

from .router import dispatch_request

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
except ImportError:
    FastAPI = None
    HTTPException = None
    BaseModel = None


class _ASGIApplication(object):
    """Minimal ASGI fallback used when FastAPI is unavailable."""

    async def __call__(self, scope, receive, send):
        if scope.get('type') != 'http':
            return

        body = b''
        more_body = True
        while more_body:
            message = await receive()
            if message.get('type') != 'http.request':
                continue
            body += message.get('body', b'')
            more_body = message.get('more_body', False)

        payload = None
        if body:
            try:
                payload = json.loads(body.decode('utf-8'))
            except ValueError:
                status_code = 400
                data = {'error': {'message': 'Request body must be valid JSON.'}}
                await _send_json(send, status_code, data)
                return

        status_code, data, content_type = dispatch_request(
            scope.get('method', 'GET'),
            scope.get('path', '/'),
            payload,
        )
        if content_type.startswith('application/json'):
            await _send_json(send, status_code, data)
        else:
            await _send_text(send, status_code, data, content_type)


async def _send_json(send, status_code, data):
    body = json.dumps(data).encode('utf-8')
    await send({
        'type': 'http.response.start',
        'status': status_code,
        'headers': [
            (b'content-type', b'application/json'),
            (b'content-length', str(len(body)).encode('ascii')),
        ],
    })
    await send({'type': 'http.response.body', 'body': body})


async def _send_text(send, status_code, data, content_type):
    body = data.encode('utf-8')
    await send({
        'type': 'http.response.start',
        'status': status_code,
        'headers': [
            (b'content-type', content_type.encode('utf-8')),
            (b'content-length', str(len(body)).encode('ascii')),
        ],
    })
    await send({'type': 'http.response.body', 'body': body})


if FastAPI is not None and BaseModel is not None:
    class ChatRequest(BaseModel):
        """Chat completion request."""

        model: str
        messages: list
        temperature: float = 0.2
        max_tokens: int = 1024


    class EmbeddingRequest(BaseModel):
        """Embedding request."""

        model: str
        input: list


    _fastapi_app = FastAPI(title='RealAI')

    @_fastapi_app.get('/health')
    def health():
        status_code, data, _ = dispatch_request('GET', '/health')
        return data

    @_fastapi_app.get('/metrics')
    def metrics():
        status_code, data, _ = dispatch_request('GET', '/metrics')
        return data

    @_fastapi_app.post('/v1/chat/completions')
    def chat(request: ChatRequest):
        status_code, data, _ = dispatch_request('POST', '/v1/chat/completions', request.dict())
        if status_code >= 400 and HTTPException is not None:
            raise HTTPException(status_code=status_code, detail=data.get('error', {}).get('message', 'Unknown error'))
        return data

    @_fastapi_app.post('/v1/embeddings')
    def embeddings(request: EmbeddingRequest):
        status_code, data, _ = dispatch_request('POST', '/v1/embeddings', request.dict())
        if status_code >= 400 and HTTPException is not None:
            raise HTTPException(status_code=status_code, detail=data.get('error', {}).get('message', 'Unknown error'))
        return data

    app = _fastapi_app
else:
    app = _ASGIApplication()


def wsgi_app(environ, start_response):
    """WSGI entrypoint for the structured server."""
    method = environ.get('REQUEST_METHOD', 'GET')
    path = environ.get('PATH_INFO', '/')
    payload = None
    content_length = environ.get('CONTENT_LENGTH') or '0'
    try:
        body_size = int(content_length)
    except ValueError:
        body_size = 0
    if body_size > 0:
        raw_body = environ['wsgi.input'].read(body_size)
        if raw_body:
            try:
                payload = json.loads(raw_body.decode('utf-8'))
            except ValueError:
                status_code = 400
                body = json.dumps({'error': {'message': 'Request body must be valid JSON.'}}).encode('utf-8')
                start_response('400 Bad Request', [
                    ('Content-Type', 'application/json'),
                    ('Content-Length', str(len(body))),
                ])
                return [body]

    status_code, data, content_type = dispatch_request(method, path, payload)
    if content_type.startswith('application/json'):
        body = json.dumps(data).encode('utf-8')
    else:
        body = data.encode('utf-8')
    start_response('{0} {1}'.format(status_code, _reason_phrase(status_code)), [
        ('Content-Type', content_type),
        ('Content-Length', str(len(body))),
    ])
    return [body]


def _reason_phrase(status_code):
    """Return a simple HTTP reason phrase."""
    if status_code == 200:
        return 'OK'
    if status_code == 400:
        return 'Bad Request'
    if status_code == 404:
        return 'Not Found'
    return 'Internal Server Error'


def main(host='0.0.0.0', port=8000):
    """Run the structured WSGI server."""
    httpd = make_server(host, int(port), wsgi_app)
    print('Structured RealAI server listening on http://{0}:{1}'.format(host, port))
    httpd.serve_forever()


if __name__ == '__main__':
    main()
