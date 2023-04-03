import uuid

from typing import BinaryIO, Optional


import cloudinary
from cloudinary.api import resource
from cloudinary.uploader import upload

from config import settings

cloudinary.config(
    cloud_name=settings.cloudinary_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret,
    secure=True
)


def upload_image(file: BinaryIO) -> Optional[str]:
    """
    The upload_image function takes a file object and uploads it to Cloudinary.
    It returns the public ID of the uploaded image.

    :param file: BinaryIO: Pass the file to be uploaded
    :return: A string
    """
    image_identifier = uuid.uuid4().hex
    file_id = settings.cloudinary_folder + image_identifier

    try:
        upload(file, public_id=file_id, owerwrite=True)
    except cloudinary.exceptions.Error as e:
        return

    return image_identifier


def get_format_image(image_identifier: str, width: int = 250, height: int = 250, crop: str = 'fill') -> Optional[str]:
    """
    The get_format_image function takes a file_id, width, height and crop as parameters.
    The function returns the url of an image with the given dimensions and cropping mode.

    :param file_id: str: Identify the image in cloudinary
    :param width: int: Set the width of the image
    :param height: int: Set the height of the image
    :param crop: str: Crop the image
    :return: The url of the image with the specified width, height and crop
    """
    file_id = settings.cloudinary_folder + image_identifier
    try:
        url = cloudinary.CloudinaryImage(file_id).build_url(
            width=width,
            height=height,
            crop=crop,
            version=resource(file_id)['version']
        )
    except cloudinary.exceptions.Error as e:
        return

    return url
