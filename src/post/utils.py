
from typing import Optional
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import Like, Post, get_async_session





# Получение поста по id 
async def get_post_by_id(post_id: int, session: AsyncSession = Depends(get_async_session)):
    statement = select(Post).where(Post.id == post_id)
    result = await session.execute(statement)
    post = result.scalar_one()
    return post  

# Проверка ставил ли лайк пользователь на пост
async def get_like_by_post_and_user(
        post_id: int, 
        user_name: str, 
        session: AsyncSession
        ) -> Optional[Like]:
    query = select(Like).where(Like.post_id == post_id, Like.user_name == user_name)
    result = await session.execute(query)
    like = result.scalar_one_or_none()
    return like
