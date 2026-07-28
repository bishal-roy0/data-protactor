"""Vercel FastAPI entry point.

Vercel detects an ``app`` object in this supported location and serves the
same Sentinel AI application used by local Uvicorn and Render deployments.
"""

from sentinel_ai.main import app
