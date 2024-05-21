from __future__ import annotations

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers.api import api_router
from app.routers.static import static_router

app = FastAPI(
    title="FeedVault API",
    description="An API for FeedVault.",
    version="0.1.0",
    openapi_url="/api/v1/openapi.json",
    redoc_url=None,
    debug=True,
)


app.mount(path="/static", app=StaticFiles(directory="static"), name="static")
app.include_router(router=api_router)
app.include_router(router=static_router)


if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=8000)  # noqa: S104
