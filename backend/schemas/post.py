from pydantic import BaseModel
from datetime import datetime


class PostBase(BaseModel):
    content: str


class PostCreate(PostBase):
    # university and college will be automatically pulled from the user's profile
    pass


class PostOut(PostBase):
    id: int
    user_id: int
    created_at: datetime
    votes_count: int

    university: str
    college: str
    major: str

    model_config = {"from_attributes": True}