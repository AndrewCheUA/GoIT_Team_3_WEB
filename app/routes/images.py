import asyncio
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connect import get_db
from app.database.models import User
from app.repository import images as repository_images
from app.schemas.image import (
    ImageCreateResponse,
    ImageGetResponse,
    ImageUpdateResponse,
    ImageDeleteResponse
)
from app.services import cloudinary
from app.services.auth import auth_service


router = APIRouter(prefix="/images", tags=["images"])


@router.post("/", response_model=ImageCreateResponse, dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def upload_image(file: UploadFile = File(), description: str = Form(min_length=10, max_length=1200),
                       db: AsyncSession = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    """
    The upload_image function is used to upload an image to the cloudinary server.
    The function takes in a file, description and database session as parameters.
    It then uses the cloudinary library to upload the image and returns a response with
    the uploaded image's id.

    :param file: UploadFile: Get the file from the request body
    :param description: str: Get the description of the image from the request body
    :param db: AsyncSession: Get the database session
    :param current_user: User: Get the user id of the current logged in user
    :return: A dict with the following keys:
    """
    loop = asyncio.get_event_loop()
    file_id = await loop.run_in_executor(None, cloudinary.upload_image, file.file)

    if file_id is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid image file")

    image = await repository_images.create_image(current_user.id, description, file_id, db)

    return {"image": image, "detail": "Image successfully created"}



@router.get("/", response_model=ImageGetResponse, dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_image(file_id: str, current_user: User = Depends(auth_service.get_current_user)):
    """
    The get_image function gets the image from Cloudinary.

    :param file_id: str: Get the file_url to download
    :param current_user: User: Get the user id of the current logged in user 
    :return: image url
    """
    if current_user:
        loop = asyncio.get_event_loop()
        url = await loop.run_in_executor(None, cloudinary.get_format_image, file_id)
    if url is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Url does not exist")

    return url


@router.put("/description", response_model=ImageUpdateResponse, dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def update_description(image_id: int, description: str = Form(min_length=10, max_length=1200), db: AsyncSession = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    """
    The update_description function updates the description of an image.
        The function takes in the description to be updated.
        It also takes in a database session and current_user (the user who is making this request).

    :param image_id: int: Get the image identifier      
    :param description: Form: Get the description
    :param db: AsyncSession: Get the database session
    :param current_user: User: Get the current user from the database
    :return: An image object
    """
    updated_image = await repository_images.update_description(current_user, image_id, description, db)
        
    if updated_image is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid identifier")

    return {"image": updated_image, "detail": "The Image was successfully updated"}


@router.delete("/", response_model=ImageDeleteResponse, dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def delete_image(image_id: int, db: AsyncSession = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    """
    The delete_image function deletes an image.
        The function takes in an identifier of the image to be deleted.
        It also takes in a database session and current_user (the user who is making this request).

    :param image_id: int: Get the image identifier  
    :param db: AsyncSession: Get the database session
    :param current_user: User: Get the current user from the database
    :return: The deleted image object
    """
    deleted_image = await repository_images.delete_image(current_user, image_id, db)
        
    if deleted_image is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid identifier")

    return deleted_image
