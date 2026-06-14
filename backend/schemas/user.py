from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime


class UserBase(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: EmailStr 
    university: str
    college: str
    major: str


class UserCreate(UserBase):
    password: str 


class UserOut(UserBase):
    id: int
    created_at: datetime
    last_username_change: datetime

    model_config = ConfigDict(from_attributes=True)