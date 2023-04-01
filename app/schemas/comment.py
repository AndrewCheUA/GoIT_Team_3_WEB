from pydantic import validator, constr

from .core import CoreModel


class CommentBase(CoreModel):
    user_id: int
    image_id: int
    data: str

    @validator('data')
    def text_must_not_be_empty(cls, value):
        if not value or not value.strip():
            raise ValueError('Text must not be empty')
        return value


class CommentUpdate(CommentBase):
    data: str


class CommentResponse(CommentBase):
    id: int = 1
    user_id: int = 1
    image_id: int = 1
    data: str = "This is a comment"

    class Config:
        orm_mode = True
