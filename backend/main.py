from fastapi import FastAPI

from backend.database import engine
from backend.models import user, post
from backend.routes import auth, posts

app = FastAPI(
    title="Elna API",
    description="Academic Platform API for managing courses, users, and authentication.",
    version="1.0.0",
)


user.Base.metadata.create_all(bind=engine)
post.Base.metadata.create_all(bind=engine)


app.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"],
)

 
app.include_router(
    posts.router,
    prefix="/posts",
    tags=["Posts"],
)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}