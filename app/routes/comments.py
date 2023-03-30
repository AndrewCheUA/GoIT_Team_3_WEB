from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connect import get_db
from app.database.models.users import UserRole
from app.services.auth import auth_service

from app.repository import comments as repository_comments

router = APIRouter()


@router.delete("/users/comments/{comment_id}")
async def delete_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserRole = Depends(auth_service.get_current_user),
) -> dict:
    """
    Delete a comment by ID.
    """
    if current_user not in [UserRole.admin, UserRole.moderator]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    comment = await repository_comments.get_comment_by_id(comment_id, db)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    await repository_comments.delete_comment(comment, db)
    return {"message": "Comment deleted successfully"}
