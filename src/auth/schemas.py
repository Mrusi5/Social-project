
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User_I(BaseModel):
    name: str
    email: str | None = None
    disabled: bool | None = None


class UserInDB(User_I):
    hashed_password: str

    class Config:
        orm_mode=True


class UserCreate(BaseModel):
    name: str
    email: str 
    password: str    