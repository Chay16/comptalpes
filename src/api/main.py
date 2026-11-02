from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from .routers import api_trips

app = FastAPI()

app.include_router(api_trips.router)


@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(
                include_url=False, include_context=False, include_input=False
            )
        },
    )
