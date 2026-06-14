from fastapi import FastAPI

from backend.database import engine
from backend.models import user as models
from backend.routes import auth

app = FastAPI(
    title="Elna API",
    description="Academic Platform API for managing courses, users, and authentication.",
    version="1.0.0",
)


models.Base.metadata.create_all(bind=engine)


app.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"],
)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}