from fastapi import Request
from fastapi.responses import JSONResponse


async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Return a safe, consistent response for unexpected server errors."""

    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected server error occurred.",
            "path": request.url.path,
        },
    )
