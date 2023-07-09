from fastapi_users.authentication import CookieTransport, JWTStrategy, AuthenticationBackend
from src.dependencies import has_access
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends
from fastapi_users.authentication import BearerTransport


cookie_transport = CookieTransport(cookie_max_age=3600)



bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")   

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET_KEY, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)   

# Конфигурация для авторизации и создания токенов
SECRET_KEY = "16f9abeb096cfd36e61db347436e34f782573a5d6a028c6a3fc0ec72a1150f4e"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 360


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

PROTECTED = [Depends(has_access)]