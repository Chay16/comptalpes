from fastapi import FastAPI

from .routers import api_costs

app = FastAPI()

app.include_router(api_costs.router)
