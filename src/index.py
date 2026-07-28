"""Vercel FastAPI entry point.

Vercel detects an ``app`` object in this supported location and serves the
same Sentinel AI application used by local Uvicorn and Render deployments.
"""

import sys
from pathlib import Path

source_directory = Path(__file__).parent
if str(source_directory) not in sys.path:
    sys.path.insert(0, str(source_directory))

from sentinel_ai.main import app
