from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import engine, Base
from backend.models import user, post, course
from backend.routes import auth, posts

app = FastAPI(
    title="Elna API",
    description="Academic Platform API for managing courses, users, and authentication.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # later we can restrict this to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(posts.router, prefix="/posts", tags=["Posts"])

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}