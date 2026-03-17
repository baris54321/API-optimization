from datetime import datetime
from pydantic import BaseModel


class CommentOut(BaseModel):
    id: int
    text: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PostOut(BaseModel):
    id: int
    title: str
    body: str
    created_at: datetime
    updated_at: datetime
    comments: list[CommentOut] = []

    model_config = {"from_attributes": True}


class UserOut(BaseModel):
    id: int
    username: str
    email: str

    model_config = {"from_attributes": True}


class UserDetailOut(BaseModel):
    user: UserOut
    posts: list[PostOut]
