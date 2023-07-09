from typing import Optional
from fastapi import APIRouter, Response
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import Like
from datetime import datetime
from fastapi import Depends, Request, status, Form
from sqlalchemy import select
from src.auth.utils import is_authenticated, get_user_name_from_token
from src.database import Like, Post, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import RedirectResponse
from fastapi.responses import HTMLResponse
from src.post.utils import get_like_by_post_and_user
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from src.post.utils import get_post_by_id


router = APIRouter(
    prefix="/post",
    tags=["post"]
)

templates = Jinja2Templates(directory="src/templates")




@router.get("/createpost", response_class=HTMLResponse)
async def createpost(
    request: Request
    ):
    if not is_authenticated(request):
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    context = {
        'is_authenticated': is_authenticated(request),
        'request': request,
    }
    return templates.TemplateResponse("createpost.html", context)

# Функция для создания нового поста
@router.post("/createpost")
async def create_post(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    session: AsyncSession = Depends(get_async_session)
    ):
    if not is_authenticated(request):
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    user_name = get_user_name_from_token(request, token=request.cookies.get("access_token"))
    created_at = datetime.utcnow()
    post = Post(user_name=user_name, created_at=created_at, title=title, content=content)
    session.add(post)
    await session.commit()
    return RedirectResponse(url="/home", status_code=status.HTTP_302_FOUND)






@router.get("/update/{post_id}", response_class=HTMLResponse)
async def updatepost(
    post_id: int,
    request: Request,
    session: AsyncSession = Depends(get_async_session)
):
    if not is_authenticated(request):
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    post = await session.execute(select(Post).filter(Post.id == post_id))
    post = post.scalar()
    if not post:
        return JSONResponse({"message": "Post not found"}, status_code=404)

    user_name = get_user_name_from_token(request, token=request.cookies.get("access_token"))
    if not user_name:
        return JSONResponse({"message": "Unauthorized"}, status_code=401)

    context = {
        'is_authenticated': is_authenticated(request),
        'request': request,
        'post': post,
        'user_name': user_name
    }
    return templates.TemplateResponse("updatepost.html", context)


# Функция для редактирования существующего поста
@router.post("/update/{post_id}", response_class=HTMLResponse)
async def update_post(
    post_id: int,
    request: Request,
    session: AsyncSession = Depends(get_async_session)
):
    if not is_authenticated(request):
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    post = await session.execute(select(Post).filter(Post.id == post_id))
    post = post.scalar()
    if not post:
        return JSONResponse({"message": "Post not found"}, status_code=404)

    user_name = get_user_name_from_token(request, token=request.cookies.get("access_token"))
    if not user_name:
        return JSONResponse({"message": "Unauthorized"}, status_code=401)

    # Обработка POST запроса
    if request.method == "POST":
        form = await request.form()
        title = form.get("title")
        content = form.get("content")

        # Обновление поста
        post.title = title
        post.content = content

        await session.commit()


    context = {
        'is_authenticated': is_authenticated(request),
        'request': request,
        'post': post,
        'user_name': user_name
    }
    return JSONResponse({"message": "Post update"}, status_code=200)








# Функция для удаления существующего поста
@router.delete("/delete/{post_id}")
async def delete_post(
    request: Request, 
    post_id: int, 
    session: AsyncSession = Depends(get_async_session)
    ):
    if not is_authenticated(request):
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    post = await session.execute(select(Post).filter(Post.id == post_id))
    post = post.scalar()
    user_name = get_user_name_from_token(request, token=request.cookies.get("access_token"))
    if not post:
        return JSONResponse({"message": "Post not found"}, status_code=404)

    if post.user_name != user_name:
        return JSONResponse({"message": "You are not the author of this post"}, status_code=403)
    
    await session.execute(delete(Like).where(Like.post_id == post_id))

    await session.delete(post)
    await session.commit()

    redirect_response = RedirectResponse(url='/home')
    redirect_response.set_cookie(key="deleted", value="true") # Устанавливаем cookie для передачи информации об удаленном посте

    return JSONResponse({"message": "Post deleted successfully"})









# Функция для постановки лайка на пост
@router.post("/{post_id}/like")
async def like_post(
    request: Request, 
    post_id: int, 
    session: AsyncSession = Depends(get_async_session)
    ):
    if not is_authenticated(request):
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    post = await get_post_by_id(post_id, session)
    user_name = get_user_name_from_token(request, token=request.cookies.get("access_token"))
    if not post:
        return JSONResponse({"message": "Post not found"}, status_code=404)
    
    if post.user_name == user_name:
        return JSONResponse({"message": "User cannot like their own post"}, status_code=400)
    
    existing_like = await get_like_by_post_and_user(post_id, user_name, session)
    if existing_like:
        return JSONResponse({"message": "User has already liked this post"}, status_code=400)
    
    post.like += 1
    like_add = Like(post_id=post_id, user_name=user_name)
    
    session.add(like_add)
    await session.commit()
    session.refresh(post)
    
    return JSONResponse({
        'post_id': post.id,
        'likes': post.like,
        'user_name': user_name
    })







# Просмотр поста
@router.get("/{post_id}")
async def get_posts(
    request: Request, 
    response: Response,
    post_id: int,
    session: AsyncSession = Depends(get_async_session)
    ):
    if not is_authenticated(request):
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)

    post = await get_post_by_id(post_id, session)
    user_name = get_user_name_from_token(request, token=request.cookies.get("access_token"))
    context = {
        'is_authenticated': is_authenticated(request),
        'request': request,
        'response': Response,
        'post' : post,
        'user_name': user_name
    }
    return templates.TemplateResponse("viewpost.html", context)