from urllib.parse import urljoin
from pydantic import Field, validator
from config import settings
from .core import CoreModel, IDModelMixin, DateTimeModelMixin


class ImageBase(CoreModel):
    """
    Leaving salt from base model
    """
    url: str = Field(..., alias='public_id')
    description: str
    user_id: str

    @validator('url', pre=True, allow_reuse=True)
    def convert_from_integer_to_currency_sum(cls, file_id: str):
        cloudinary_base_url = "https://res.cloudinary.com"
        version = "v999999999"
        url = f"{settings.cloudinary_name}/upload/{version}/{file_id}"

        return urljoin(cloudinary_base_url, url)


class ImagePublic(DateTimeModelMixin, ImageBase, IDModelMixin):
    class Config:
        orm_mode = True


class ImageCreateResponse(CoreModel):
    image: ImagePublic
    detail: str = "The Image was successfully created"
    class Config:
        orm_mode = True


class ImageGetResponse(CoreModel):
    detail: str = "The Image was successfully got"
    class Config:
        orm_mode = True


class ImageUpdateResponse(CoreModel):
    image: ImagePublic
    detail: str = "The Image was successfully updated"
    class Config:
        orm_mode = True  


class ImageDeleteResponse(CoreModel):
    detail: str = "The Image was successfully deleted"
    class Config:
        orm_mode = True           
