from datetime import datetime, timedelta
from typing import Annotated, Union
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy import select
from src.auth.schemas import TokenData, User_I, UserInDB
from src.auth.models import user
from src.database import User, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.base_config import ALGORITHM, SECRET_KEY, pwd_context, oauth2_scheme
from jwt.exceptions import ExpiredSignatureError, DecodeError


# Функция для проверки соответствия паролей
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Функция для получения хеша пароля
def get_password_hash(password):
    return pwd_context.hash(password)

# Функция для поиска пользователя в базе данных по имени пользователя
async def get_user(
        username: str, 
        session: AsyncSession = Depends(get_async_session)
        ) -> UserInDB:
    query = select(user).where(user.c.name == username)
    result = await session.execute(query)
    user_get = result.fetchone()
    if not user_get:
        return None
    user_r = UserInDB.from_orm(user_get)
    user_dict = user_r.dict()

    return user_dict

# Функция для аутентификации пользователя при запросе токена доступа
async def authenticate_user(
        form_data: OAuth2PasswordRequestForm, 
        session: AsyncSession = Depends(get_async_session)
        ) -> Union[UserInDB, None]:
    user_get = await get_user(form_data.username, session)
    if user_get is None:
        return False
    user_r = UserInDB(**user_get)
    if not user_r:
        return False
    if not verify_password(form_data.password, user_r.hashed_password):
        return False
    return user_r

# Функция для создания токена доступа
def create_access_token(
        data: dict, 
        expires_delta: timedelta | None = None
        ):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Функция для получения текущего пользователя по токену доступа
async def get_current_user(
        token: Annotated[str, 
        Depends(oauth2_scheme)], 
        session: AsyncSession = Depends(get_async_session)
        ) -> User_I:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user_r = await get_user(token_data.username, session)
    if user_r is None:
        raise credentials_exception
    return user_r

# Функция для получения текущего активного пользователя по токену доступа
async def get_current_active_user(
    current_user: User_I = Depends(get_current_user)
):
    user_r = User_I(**current_user)
    if user_r.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def is_authenticated(request: Request) -> bool:
    token = request.cookies.get("access_token")
    if not token:
        return False

    try:
        jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        return True
    except ExpiredSignatureError:
        return False
    except DecodeError:
        return False
# Получение имени из токена    
def get_user_name_from_token(
        request: Request, 
        token: str) -> int:
    token = request.cookies.get("access_token")
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_name: str = payload.get("sub") 

    return user_name 


# Получение id по имени(имена уникальны)
async def get_user_id_by_name(
        username, 
        session: AsyncSession = Depends(get_async_session)):
    query = select(User.id).where(User.username == username)
    result = await session.execute(query).scalar()

    return result