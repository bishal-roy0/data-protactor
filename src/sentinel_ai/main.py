from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from sentinel_ai.api.routes import router
from sentinel_ai.core.config import get_settings
from sentinel_ai.core.errors import unhandled_exception_handler


def create_application() -> FastAPI:
    """Build and configure the Sentinel AI ASGI application."""

    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        description="AI-powered security analysis for communication content.",
        version="0.1.0",
    )
    application.include_router(router)
    application.add_exception_handler(Exception, unhandled_exception_handler)
    web_directory = Path(__file__).parent / "web"
    application.mount("/assets", StaticFiles(directory=web_directory / "assets"), name="assets")

    @application.get("/", include_in_schema=False)
    async def dashboard() -> FileResponse:
        return FileResponse(web_directory / "index.html")

    return application


app = create_application()
