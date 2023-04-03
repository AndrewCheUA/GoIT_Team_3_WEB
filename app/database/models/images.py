from datetime import datetime
from typing import Optional

from sqlalchemy import (
    func,
    String,
    ForeignKey,
    Integer,
    Table,
    Column,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref, Session

from .base import Base
from .users import User


image_m2m_tag = Table(
    "image_m2m_tag",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("image_id", Integer, ForeignKey("images.id", ondelete="CASCADE")),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE")),
)


class Image(Base):
    __tablename__ = 'images'

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(1200))
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    average_rating: Mapped[float] = mapped_column(default=0)

    user: Mapped[User] = relationship(backref="images")
    tags = relationship("Tag", secondary=image_m2m_tag, backref="images")
    ratings = relationship("PhotoRating", cascade="all, delete-orphan", backref=backref("image"))

    def update_average_rating(self):
        """
        The update_average_rating function updates the average rating of a photo.
        It does this by iterating through all ratings associated with the photo, and then calculating an average based on those ratings.

        :param self: Refer to the object itself
        :return: The average rating of a photo
        :doc-author: Trelent
        """
        total_rating = 0
        num_ratings = 0
        for rating in self.ratings:
            total_rating += rating.photo_rating
            num_ratings += 1
        if num_ratings > 0:
            self.average_rating = total_rating / num_ratings
        else:
            self.average_rating = 0

    @staticmethod
    async def get_image_by_id(db_session: Session, image_id: int) -> Optional["Image"]:
        return await db_session.query(Image).filter(Image.id == image_id).first()
