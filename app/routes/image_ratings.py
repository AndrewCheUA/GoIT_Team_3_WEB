from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.database.connect import get_db
from app.database.models import User, Image
from app.database.models.image_raiting import ImageRating
from app.models.image_raitings import ImageRatingCreate, ImageRatingUpdate
from app.services.auth import auth_service


router = APIRouter()


@router.post("/{image_id}/ratings", response_model=ImageRating)
async def create_image_rating(
    image_id: int,
    rating_data: ImageRatingCreate,
    current_user: User = Depends(auth_service.get_current_user),
    db_session = Depends(get_db)
):
    image = await Image.get_image_by_id(db_session, image_id)
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    if image.user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot rate own image")
    rating = await ImageRating.create(db_session, **rating_data.dict(), image_id=image_id, user_id=current_user.id)
    return rating


@router.put("/{image_id}/ratings/{rating_id}", response_model=ImageRating)
async def update_image_rating(
    rating_id: int,
    rating_data: ImageRatingUpdate,
    current_user: User = Depends(auth_service.get_current_user),
    db_session=Depends(get_db),
):
    rating = await ImageRating.get_rating_by_id(db_session, rating_id)
    if not rating:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found")
    if rating.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    rating = await rating.update(db_session, **rating_data.dict())
    return rating


@router.delete("/ratings/{rating_id}")
async def delete_image_rating(
        rating_id: int,
        current_user: User = Depends(auth_service.get_current_user),
        db_session=Depends(get_db)
):
    rating = await ImageRating.get_rating_by_id(db_session, rating_id)
    if not rating:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found")

    if auth_service.is_admin_or_moderator(current_user):
        await ImageRating.delete_rating_by_id(db_session, rating_id)
    elif rating.user_id == current_user.id:
        await ImageRating.delete_rating_by_id(db_session, rating_id)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    return {"message": "Rating deleted"}


@router.get("/{image_id}/ratings", response_model=List[ImageRating])
async def get_all_image_ratings(image_id: int, db_session = Depends(get_db)):
    ratings = await ImageRating.get_all_ratings(db_session, image_id)
    return ratings
