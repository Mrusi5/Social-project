from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Cookie, Depends, Request, Response, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from src.auth.base_config import ACCESS_TOKEN_EXPIRE_MINUTES
from src.auth.utils import authenticate_user, create_access_token, get_password_hash, get_user, is_authenticated
from src.database import Post, get_async_session, User
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import RedirectResponse
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates




router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

templates = Jinja2Templates(directory="src/templates")


@router.get("/register", response_class=HTMLResponse)
async def register(
    request: Request
    ):
    return templates.TemplateResponse("register.html", {"request": request})

# Регистрация пользователя
@router.post("/register", response_class=HTMLResponse)
async def register_user(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(get_async_session)
    ):
    # Проверка наличия пользователя в базе
    user_get = await get_user(name, session)
    if user_get:
        return templates.TemplateResponse('register.html', {'request': request, 'error_message': 'Username already registered'})
    # Хеширование пароля и создание объекта пользователя в базе
    hashed_password = get_password_hash(password)
    user_obj = User(name=name, email=email, hashed_password=hashed_password)
    session.add(user_obj)
    await session.commit()
    return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)








@router.get("/login", response_class=HTMLResponse)
async def login(
    request: Request
    ):
    return templates.TemplateResponse("login.html", {"request": request})

# Авторизация пользователя и получение токена доступа
@router.post("/login", response_class=HTMLResponse)
async def login_for_access_token(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_async_session)
):
    user_auth = await authenticate_user(form_data, session)
    if not user_auth:
        return templates.TemplateResponse('login.html', {'request': request, 'error_message': 'Incorrect username or password'})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_auth.name}, expires_delta=access_token_expires
    )
    response = RedirectResponse(url="/home", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=access_token)
    return response







# Функция выхода с аккаунта
@router.post("/logout")
async def logout(
    request: Request, 
    response: Response, 
    session_token: str = Cookie(None)
    ):
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="session_token")
    response.status_code = status.HTTP_302_FOUND
    response.headers["Location"] = "/auth/login"
    return response