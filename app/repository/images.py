from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import Image, User
from sqlalchemy import update, and_, delete
from typing import Optional
from sqlalchemy.orm.exc import UnmappedInstanceError


async def create_image(user_id: int, description: str, uuid: str, db: AsyncSession) -> Image:
    """
    The create_image function creates a new image in the database.

    :param user_id: int: Identify the user who uploaded the image
    :param description: str: Set the description of the image
    :param uuid: str: Identify the image
    :param db: AsyncSession: Pass in the database session to be used
    :return: An image object
    """
    image = Image(
        user_id=user_id,
        description=description,
        uuid=uuid
    )
    db.add(image)

    await db.commit()
    await db.refresh(image)

    return image


async def update_description(current_user: User, image_id: int, description: str, db: AsyncSession) -> Optional[Image]:
    """
    The update_description function updates the image's description in the database.

    :param current_user: int: Get the current user
    :param description: str: Get description for image
    :param image_id: str: Get hash for image
    :param db: AsyncSession: Pass in the database session to the function
    :return: An image object
    """
    try:
        async with db.begin():
            image = await db.scalar(
                update(Image)
                .values(description=description)
                .filter(and_(Image.user_id == current_user.id, Image.id == image_id))
                .returning(Image)
            )
            await db.commit()
        await db.refresh(image)

    except UnmappedInstanceError:
        ...        

    return image


async def delete_image(current_user: User, image_id: int, db: AsyncSession) -> Optional[Image]:
    """
    The delete_image function deletes an image in the database.

    :param current_user: int: Get the current user
    :param image_id: str: Get identifier for the image
    :param db: AsyncSession: Pass in the database session to the function
    :return: An image object
    """
    try:
        async with db.begin():
            image = await db.scalar(
                delete(Image)
                .filter(and_(Image.user_id == current_user.id, Image.id == image_id))
                .returning(Image)
            )
    except UnmappedInstanceError:
        ...        

    return image
