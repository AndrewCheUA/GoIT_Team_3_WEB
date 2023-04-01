from sqlalchemy.orm import relationship

from .base import Base
from .images import Image


class TransformedImage(Base):
    __tablename__ = "images_urls"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    url: Mapped[str] = mapped_column(String(100), nullable=False)
    image_id: Mapped[int] = mapped_column(ForeignKey("images.id"), nullable=False)
    image: Mapped[Image] = relationship(backref = "images_urls")

