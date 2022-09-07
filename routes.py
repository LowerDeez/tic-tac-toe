from starlette.routing import Route, Mount, WebSocketRoute
from starlette.staticfiles import StaticFiles

from endpoints import Index
from ws import WebSockerGameWrapper


routes = [
    Route('/', Index),
    WebSocketRoute('/ws', WebSockerGameWrapper),
    Mount('/static/', StaticFiles(directory="static"))
]
