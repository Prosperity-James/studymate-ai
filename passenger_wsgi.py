"""
Entry point for cPanel's "Setup Python App" (Phusion Passenger).
Passenger 6+ supports ASGI apps directly — it detects that `application`
is an ASGI callable (not a WSGI one) and serves it accordingly, no adapter
needed for FastAPI.
"""
from app.main import app as application
