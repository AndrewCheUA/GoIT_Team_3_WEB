import asyncio

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connect import get_db
from app.database.models import User, UserRole
from app.repository import users as repository_users
from app.models.user import (
    UserPublic,
    UserPasswordUpdate,
    EmailModel,
)
from app.services import cloudinary
from app.services.auth import auth_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserPublic, dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_me(current_user: User = Depends(auth_service.get_current_user)):
    """
    The get_me function returns the current user.

    :param current_user: User: Get the current user
    :return: The current user object
    """
    return current_user


@router.patch("/avatar", response_model=UserPublic, dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def update_avatar(file: UploadFile = File(), db: AsyncSession = Depends(get_db),
                        current_user: User = Depends(auth_service.get_current_user)):
    """
    The update_avatar function updates the avatar of a user.

    :param file: UploadFile: Get the file that is uploaded
    :param db: AsyncSession: Get the database session
    :param current_user: User: Get the current user
    :return: The updated user object
    """
    loop = asyncio.get_event_loop()
    file_id = await loop.run_in_executor(None, cloudinary.upload_image, file.file)
    avatar_url = await loop.run_in_executor(None, cloudinary.get_format_image, file_id)

    return await repository_users.update_avatar(current_user.id, avatar_url, db)


@router.patch("/email", response_model=UserPublic, dependencies=[Depends(RateLimiter(times=2, seconds=60))])
async def update_email(body: EmailModel, db: AsyncSession = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    """
    The update_email function updates the email of a user.
        The function takes in an EmailModel object, which contains the new email address to be updated.
        It also takes in a database session and current_user (the user who is making this request).

    :param body: EmailModel: Get the email from the request body
    :param db: AsyncSession: Get the database session
    :param current_user: User: Get the current user from the database
    :return: A user object
    """
    updated_user = await repository_users.update_email(current_user.id, body.email, db)

    if updated_user is None:
        return HTTPException(status_code=status.HTTP_409_CONFLICT,
                             detail="An account with this email address already exists")

    return updated_user


@router.patch("/password", response_model=UserPublic, dependencies=[Depends(RateLimiter(times=2, seconds=60))])
async def update_password(body: UserPasswordUpdate, db: AsyncSession = Depends(get_db),
                          current_user: User = Depends(auth_service.get_current_user)):
    """
    The update_password function takes in a ChangePassword object, which contains the old and new passwords.
    It then verifies that the old password is correct, hashes the new password, and updates it in the database.

    :param body: ChangePassword: Pass the old and new password to the function
    :param db: AsyncSession: Get the database session
    :param current_user: User: Get the user that is currently logged in
    :return: A dictionary with the following keys:
    """
    if not auth_service.verify_password(body.old_password, current_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid old password")

    password = auth_service.get_password_hash(body.new_password)

    return await repository_users.update_password(current_user.id, password, db)


@router.post("/change-role", dependencies=[Depends(auth_service.get_current_user), Depends(UserRole.admin)])
async def change_user_role(user_id: int, db: AsyncSession = Depends(get_db)):
    """
    The change_user_role function changes the role of a user.
    Args:
        user_id (int): The id of the user to change.
        db (AsyncSession, optional): An open database session. Defaults to Depends(get_db).

    :param user_id: int: Specify the user id of the user to be deleted
    :param db: AsyncSession: Pass the database connection to the function
    :return: A dictionary with the message key and a string value
    :doc-author: Trelent
    """
    user = await repository_users.get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    await repository_users.user_update_role(user_id, db)
    return {'message': 'User role updated successfully.'}


@router.post("/users/ban/{user_id}")
async def ban_user(user_id: int, db: AsyncSession = Depends(get_db),
                   current_user: UserRole = Depends(auth_service.get_current_user)):
    """
    The ban_user function is used to ban a user.

    :param user_id: int: Specify the user id of the user to be banned
    :param db: AsyncSession: Pass the database session to the function
    :param current_user: UserRole: Get the current user's role
    :return: A dictionary with a message, which is not the right way to return data
    :doc-author: Trelent
    """
    if current_user != UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    user = await repository_users.get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.is_active = False
    await db.commit()
    return {"message": f"User {user.username} banned successfully"}
