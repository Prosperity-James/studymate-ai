"""
Entry point for cPanel's "Setup Python App" (Phusion Passenger / LSAPI).

Many shared-hosting Passenger setups (especially under LiteSpeed) only
reliably support WSGI, not raw ASGI — handing them an ASGI app directly
causes "Incomplete response received from application" errors. Wrapping
with a2wsgi's ASGIMiddleware makes the FastAPI app speak WSGI instead.
"""
from a2wsgi import ASGIMiddleware

from app.main import app as _fastapi_app

application = ASGIMiddleware(_fastapi_app)
