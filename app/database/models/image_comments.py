from typing import Optional
from datetime import datetime

from sqlalchemy import String, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .users import User
from .images import Image


class ImageComment(Base):
    __tablename__ = "image_comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    data: Mapped[str] = mapped_column(String(500), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id, ondelete="CASCADE", onupdate="CASCADE"))
    image_id: Mapped[int] = mapped_column(ForeignKey(Image.id, ondelete="CASCADE", onupdate="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(onupdate=func.now())

    user: Mapped[User] = relationship(backref="image_comments")
    image: Mapped[Image] = relationship("Image", back_populates="comments", passive_deletes=True)
