from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Comment


async def delete_comment(comment_id: int, db: AsyncSession):
    """
    The delete_comment function deletes a comment with a given id from the database.
    Args:
        comment_id (int): The id of the comment to be deleted.
        db (AsyncSession): An open database session.
    Returns:
        None.
    :doc-author: Trelent
    """
    await db.execute(
        delete(Comment)
        .where(Comment.id == comment_id)
    )
    await db.commit()
    return {'message': f'Comment {comment_id} has been deleted'}