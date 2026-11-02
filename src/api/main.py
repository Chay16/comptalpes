from fastapi import FastAPI

from .routers import api_expenses

app = FastAPI()

app.include_router(api_expenses.router)
