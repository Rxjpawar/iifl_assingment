from fastapi import Request
from fastapi.responses import JSONResponse


class AIServiceError(Exception):
    """Raised when the model cannot provide a valid content result."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class EntryNotFoundException(Exception):
    def __init__(self, entry_id: int):
        super().__init__(f"Entry {entry_id} not found.")
        self.entry_id = entry_id


# custom exception handlers for the above exceptions

async def ai_service_error_handler(request: Request, exc: AIServiceError):
    return JSONResponse(
        status_code=502,
        content={"message": exc.message},
    )


async def entry_not_found_exception_handler(request: Request, exc: EntryNotFoundException):
    return JSONResponse(
        status_code=404,
        content={"message": f"Entry {exc.entry_id} not found."},
    )
